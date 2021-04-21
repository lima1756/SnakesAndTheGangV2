import numpy as np

conditions = [('Rotate left', 1), ('Rotate right', 2),
              ('Shake horizontal', 3), ('Shake vertically', 4)]
time = 40
partioning = 0.25
rate = time/partioning

data = np.genfromtxt('data.csv', delimiter=',').tolist()


acc_data = [[], [], [], []]
gyro_data = [[], [], [], []]
magn_data = [[], [], [], []]
for i in range(4):
    acc_data[i] = np.array_split(
        [r for r in data if r[1] == 3 and r[0] == i+1], rate)
    gyro_data[i] = np.array_split(
        [r for r in data if r[1] == 4 and r[0] == i+1], rate)
    magn_data[i] = np.array_split(
        [r for r in data if r[1] == 5 and r[0] == i+1], rate)
