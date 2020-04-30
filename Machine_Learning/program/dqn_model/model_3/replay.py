import csv
import numpy as np
import matplotlib.pyplot as plt


with open('ac-control-dqn-detail.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    total_rewards = []
    rewards = 0.0
    for row in reader:
        rewards += float(row[2])
        if (row[4] == "True"):
            total_rewards.append(rewards)
            rewards = 0.0

total_rewards = np.array(total_rewards)
'''
ind = np.argpartition(total_rewards, -20)[-20:]
location = np.sort(ind).tolist()
print(location)
best_episodes = []
with open('ac-control-dqn-detail.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    index = 0
    j = 0
    for row in reader:
        if (index in location):
            modify_row = row
            modify_row[0] = modify_row[0].replace('[[', '')
            modify_row[0] = modify_row[0].replace(']]', '')
            modify_row[3] = modify_row[3].replace('[[', '')
            modify_row[3] = modify_row[3].replace(']]', '')
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
            modify_row[1], modify_row[2] = float(modify_row[1]), float(modify_row[2])
            if (modify_row[4] == 'True'):
                modify_row[4] = True
            else:
                modify_row[4] = False
            best_episodes.append(modify_row)
        if (j % 25 == 0 and j != 0):
            index += 1
        j += 1


best_episodes = np.array(best_episodes).reshape((20,25,5))
print(best_episodes.shape)

with open('best_episodes.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    for data in best_episodes:
        for row in data:
            writer.writerow(row)
'''

plt.title("Episodes Rewards")
rewards_10 = []
episodes = []
for i in range(len(total_rewards)):
    if (i % 19 == 0):
        rewards_10.append(np.mean(total_rewards[i:i+19]))
        episodes.append(i)
plt.plot(episodes, rewards_10)
plt.xlabel("Episodes")
plt.ylabel("Rewards")
plt.show()

