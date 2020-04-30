import gym
import csv
import json
import time
import numpy as np
import random
import tensorflow as tf
import matplotlib.pyplot as plt
from collections import deque
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.optimizers import Adam, RMSprop
from libs.ac_env import AC_Env
from libs import ac_host
from libs import thermal_comfort_prediction_model as thermal_comfort_model
from libs import temperature_prediction_model as temperature_model
from libs import humidity_prediction_model as humidity_model
from libs import skin_temp_prediction_model as skin_temp_model
from libs.timer import Timer

best_episodes = []
MEAN_REWARD_BOUND = 80
Parameter = {
    'MODEL_NAME' : 'AC Control Q Value Predict',
    'GAMMA' : 0.9,
    'EPISODES' : 1000,
    'TEST_EPISODES': 10,
    'BATCH_SIZE' : 32,
    'REPLAY_SIZE' : 2000,
    'LEARNING_RATE' : 0.0001,
    'SYNC_TARGET_STEPS' : 1000,
    'REPLAY_START_SIZE' : 1000,
    'EPSILON_DECAY' : 0.9996,
    'EPSILON_START' : 1.0,
    'EPSILON_FINAL' : 0.001,
}

def DQNModel(input_shape, action_space, model_name, learning_rate ):
    X_input = Input(input_shape)

    # 'Dense' is the basic form of a neural network layer
    # Input Layer of state size(4) and Hidden Layer with 1028 nodes
    X = Dense(512, input_shape=input_shape, activation="relu", kernel_initializer='he_uniform')(X_input)

    # Hidden layer with 512 nodes
    X = Dense(256, activation="relu", kernel_initializer='he_uniform')(X)

    # Hidden layer with 128 nodes
    X = Dense(64, activation="relu", kernel_initializer='he_uniform')(X)

    # Output Layer with # of actions: 27 nodes
    X = Dense(action_space, activation="linear", kernel_initializer='he_uniform')(X)

    model = Model(inputs = X_input, outputs = X, name=model_name)
    model.compile(loss="mse", optimizer=RMSprop(lr=learning_rate, rho=0.95, epsilon=0.01), metrics=["accuracy"])

    model.summary()
    return model



class DQNAgent:
    def __init__(self, env, **kwargs):
        self.env = env
        # by default, CartPole-v1 has max episode steps = 500
        self.state_size = self.env.observation_space.shape[0]
        self.action_size = self.env.action_space.n
        self.EPISODES = kwargs.get('EPISODES', 1000)
        self.TEST_EPISODES = kwargs.get('TEST_EPISODES', 10)
        self.replay_size = kwargs.get('REPLAY_SIZE', 2000)
        self.memory = deque(maxlen=kwargs.get('REPLAY_SIZE', 2000))

        self.permanent_data_head = 0

        self.gamma = kwargs.get('GAMMA', 0.95)    # discount rate
        self.epsilon = kwargs.get('EPSILON_START', 1.0)  # exploration rate
        self.epsilon_min = kwargs.get('EPSILON_FINAL', 0.001)
        self.epsilon_decay = kwargs.get('EPSILON_DECAY', 0.999)
        self.batch_size = kwargs.get('BATCH_SIZE', 32)
        self.train_start = kwargs.get('REPLAY_START_SIZE', 1000)
        self.sync_target_steps = kwargs.get('SYNC_TARGET_STEPS', 1000)
        self.episode_reward = []
        # create main model
        self.model = DQNModel(input_shape=(self.state_size,), action_space = self.action_size,
            model_name=kwargs.get('MODEL_NAME', 'DQN_model'), learning_rate=kwargs.get('LEARNING_RATE', 0.0001))
        self.tgt_net = DQNModel(input_shape=(self.state_size,), action_space = self.action_size,
            model_name=kwargs.get('MODEL_NAME', 'DQN_model'), learning_rate=kwargs.get('LEARNING_RATE', 0.0001))


    def update_permanent_memory(self):
        for episode in best_episodes:
            state = np.array(episode[0]).reshape((1, agent.state_size))
            action = episode[1]
            reward = episode[2]
            next_state = np.array(episode[3]).reshape((1, agent.state_size))
            done = episode[4]
            self.memory.append((state, action, reward, next_state, done))


    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        #if (len(self.memory) - self.permanent_data_head == self.replay_size and self.permanent_data_head == 0):
        #    self.update_permanent_memory()
        #    self.permanent_data_head = self.replay_size - len(best_episodes)
        #if (self.permanent_data_head != 0):
        #    self.permanent_data_head -= 1
        if len(self.memory) > self.train_start:
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay

    def act(self, state):
        if np.random.random() <= self.epsilon:
            return random.randrange(self.action_size)
        else:
            return np.argmax(self.model.predict(state))

    def replay(self):
        if len(self.memory) < self.train_start:
            return
        # Randomly sample minibatch from the memory
        minibatch = random.sample(self.memory, min(len(self.memory), self.batch_size))

        state = np.zeros((self.batch_size, self.state_size))
        next_state = np.zeros((self.batch_size, self.state_size))
        action, reward, done = [], [], []

        # do this before prediction
        # for speedup, this could be done on the tensor level
        # but easier to understand using a loop
        for i in range(self.batch_size):
            state[i] = minibatch[i][0]
            action.append(minibatch[i][1])
            reward.append(minibatch[i][2])
            next_state[i] = minibatch[i][3]
            done.append(minibatch[i][4])

        # do batch prediction to save speed
        target = self.model.predict(state)
        target_next = self.tgt_net.predict(next_state)

        for i in range(self.batch_size):
            # correction on the Q value for the action used
            if done[i]:
                target[i][action[i]] = reward[i]
            else:
                # Standard - DQN
                # DQN chooses the max Q value among next actions
                # selection and evaluation of action is on the target Q Network
                # Q_max = max_a' Q_target(s', a')
                target[i][action[i]] = reward[i] + self.gamma * (np.amax(target_next[i]))

        # Train the Neural Network with batches
        self.model.fit(state, target, batch_size=self.batch_size, verbose=0)


    def load(self, name):
        self.model = load_model(name)

    def save(self, name):
        self.model.save(name)

    def run(self):
        total_steps = 0
        for e in range(self.EPISODES):
            state = self.env.reset()
            state = np.reshape(state, [1, self.state_size])
            done = False
            i = 0
            episode_reward_acc = 0
            package = []
            isFinishTrain = False
            while not done:
                #self.env.render()
                action = self.act(state)
                next_state, reward, done, _ = self.env.step(action)
                episode_reward_acc += reward
                next_state = np.reshape(next_state, [1, self.state_size])
                reward = reward
                self.remember(state, action, reward, next_state, done)
                package.append([state, action, reward, next_state, done])
                state = next_state
                i += 1
                total_steps += 1
                if (total_steps % self.sync_target_steps == 0):
                    self.tgt_net.set_weights(self.model.get_weights())
                    print("Sync target network weight with train network")
                    total_steps = 0
                if done:
                    print("episode: {}/{}, score: {}, e: {:.2}".format(e, self.EPISODES, episode_reward_acc, self.epsilon))
                    if (episode_reward_acc > MEAN_REWARD_BOUND):
                        print("Reach mean reward bound {}".format(MEAN_REWARD_BOUND))
                        isFinishTrain = True
                self.replay()

            self.episode_reward.append(episode_reward_acc)
            with open('dqn_model/ac-control-dqn-detail.csv', 'a') as csvfile:
                writer = csv.writer(csvfile)
                for row in package:
                    writer.writerow(row)

            if (isFinishTrain):
                break

        print("Saving trained model")
        self.save("dqn_model/ac-control-dqn.h5")


    def test(self):
        self.load("dqn_model/ac-control-dqn.h5")
        for e in range(self.TEST_EPISODES):
            state = self.env.reset()
            state = np.reshape(state, [1, self.state_size])
            done = False
            i = 0
            acc_reward = 0
            while not done:
                self.env.render()
                action = np.argmax(self.model.predict(state))
                next_state, reward, done, _ = self.env.step(action)
                state = np.reshape(next_state, [1, self.state_size])
                i += 1
                acc_reward += reward
                if done:
                    print("episode: {}/{}, score: {}".format(e, self.TEST_EPISODES, acc_reward))
                    break



if __name__ == "__main__":
    host = ac_host.AC_host("fyp0001","watch0001")
    data_request_timer = Timer()
    thermal_predict_model = thermal_comfort_model.create_model()
    thermal_predict_model.load_model(path="thermal_comfort_predict_models/prediction_model_1.h5")
    temp_predict_model = temperature_model.create_model()
    temp_predict_model.load_model(path="temperature_prediction_models/prediction_model_1.h5")
    hum_predict_model = humidity_model.create_model()
    hum_predict_model.load_model(path="humidity_prediction_models/prediction_model_1.h5")
    skin_temp_model = skin_temp_model.create_model()
    skin_temp_model.load_model(path="skin_temperature_prediction_models/prediction_model_1.h5")
    isSimulate = True
    env = AC_Env(isSimulate, host, thermal_predict_model, temp_predict_model, hum_predict_model, skin_temp_model)
    if (not isSimulate):
        if (host.check_action_done()):
            host.ac_power_switch(True)
            print("Waiting AC Remote respoonse")
            while(not host.check_action_done()):
                pass
            host.update_ac_status()
            print("AC is switched ON")
    agent = DQNAgent(env, **Parameter)
    '''
    with open('dqn_model/model_3/best_episodes.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            modify_row = row
            modify_row[0] = modify_row[0].replace('[', '')
            modify_row[0] = modify_row[0].replace(']', '')
            modify_row[3] = modify_row[3].replace('[', '')
            modify_row[3] = modify_row[3].replace(']', '')
            modify_row[0] = modify_row[0].split(' ')
            while (len(modify_row[0]) != 5):
                for i in range(len(modify_row[0])):
                    if (modify_row[0][i] == ''):
                        modify_row[0].pop(i)
                        break
            for i in range(len(modify_row[0])):
                modify_row[0][i] = float(modify_row[0][i])
            modify_row[3] = modify_row[3].split(' ')
            while (len(modify_row[3]) != 5):
                for i in range(len(modify_row[3])):
                    if (modify_row[3][i] == ''):
                        modify_row[3].pop(i)
                        break
            for i in range(len(modify_row[3])):
                modify_row[3][i] = float(modify_row[3][i])
            modify_row[0], modify_row[3] = np.array(modify_row[0]), np.array(modify_row[3])
            modify_row[1], modify_row[2] = int(float(modify_row[1])), float(modify_row[2])
            if (modify_row[4] == 'True'):
                modify_row[4] = True
            else:
                modify_row[4] = False
            best_episodes.append(modify_row)
    '''
    #agent.load('dqn_model/ac-control-dqn.h5')
    agent.run()
    #agent.test()

