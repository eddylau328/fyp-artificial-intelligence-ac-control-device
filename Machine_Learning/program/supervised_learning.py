import enum
from tensorflow.keras.model import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.optimizers import Adam


class Feedback(enum.Enum):
    very_hot = 0
    hot = 1
    a_bit_hot = 2
    comfy = 3
    aceptable = 4
    a_bit_cold = 5
    cold = 6
    very_cold = 7

##############################################################
#
#       Input layers              Range              Shape
#   -indoor temperature           17-30              (1,)
#   -indoor humidity              40-100             (1,)
#   -outdoor temperature          10-40              (1,)
#   -outdoor humidity             40-100             (1,)
#   -body temperature             28-35              (1,)
#   -AC temperature setting       17-25              (1,9)  <- need one hot encoding
#   -Fanspeed setting              1-3               (1,3)  <- need one hot encoding
#
##############################################################


def SupervisedLearningModel(input_shape, output_shape, model_name, learning_rate ):
    X_input = Input(input_shape)

    # 'Dense' is the basic form of a neural network layer
    # Input Layer of state size and Hidden Layer with 512 nodes
    X = Dense(512, input_shape=input_shape, activation="relu", kernel_initializer='he_uniform')(X_input)

    # Hidden layer with 256 nodes
    X = Dense(256, activation="relu", kernel_initializer='he_uniform')(X)

    # Hidden layer with 64 nodes
    X = Dense(64, activation="relu", kernel_initializer='he_uniform')(X)

    # Output Layer with # of actions: 2 nodes (left, right)
    X = Dense(action_space, activation="linear", kernel_initializer='he_uniform')(X)

    model = Model(inputs = X_input, outputs = X, name=model_name)
    model.compile(loss="mse", optimizer=RMSprop(lr=learning_rate, rho=0.95, epsilon=0.01), metrics=["accuracy"])

    model.summary()
    return model


class SupervisedLearning:

    def __init__(self):
        self.input_size =
        self.model = SupervisedLearningModel(input_shape=(self.input_size,), output_shape = ,)
