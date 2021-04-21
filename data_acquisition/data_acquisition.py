# ------------------------------------------------------------------------------------------------------------------
#   Data acquisition program.
# ------------------------------------------------------------------------------------------------------------------
import time
import socket
import struct
import random
import numpy as np
from functools import cmp_to_key

# Experiment configuration
conditions = [('Rotate left', 1), ('Rotate right', 2),
              ('Shake horizontal', 3), ('Shake vertically', 4)]
n_trials = 4

fixation_cross_time = 2
preparation_time = 2
training_time = 10
rest_time = 2

# Experiment stages
trials = n_trials*conditions
random.shuffle(trials)

experiment = []
for tr in trials:
    experiment.append(("*********", fixation_cross_time, 0))
    experiment.append((tr[0], preparation_time, 0))
    experiment.append(('', training_time, tr[1]))
    experiment.append(('Rest', rest_time, -1))

# Socket configuration
UDP_IP = '192.168.1.104'
UDP_PORT = 8800
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(0.001)

# Data acquisition loop
trials = []
recorded_data = []  # acc, gyro, mag
start = [0, 0, 0]  # acc, gyro, mag

trial_id = 0

update_time = 0

step = -1

start_time = time.time()
while True:

    ellapsed_time = time.time() - start_time
    if ellapsed_time >= update_time:

        step = step + 1

        if step < len(experiment):
            start_time = time.time()
            print(experiment[step][0])
            update_time = experiment[step][1]

            if experiment[step][2] > 0:
                trial_id = experiment[step][2]
                start = len(recorded_data)

            elif experiment[step][2] == -1:
                trials.append([trial_id, start, len(recorded_data)])

        else:
            break

    try:
        # Read data from UDP connection
        data, addr = sock.recvfrom(1024*1024)

        # Decode binary stream.
        data_string = data.decode('ascii').split(",")

        # Append new sensor data
        nsensors = (len(data_string)-1)/4

        for ind in range(1, len(data_string), 4):
            type = int(data_string[ind])
            # type 3=accelerometer, 4=gyro, 5=magnetic
            recorded_data.append([-1, type, float(data_string[ind+1]), float(data_string[ind+2]),
                                  float(data_string[ind+3])])
        # print("ok")

    except socket.timeout:
        # print("warning, no data received")
        pass


def cmp_row(a, b):
    if(a[1] == b[1]):
        return a[0]-b[0]
    return a[1]-b[1]


for trial in trials:
    for j in range(trial[1], trial[2]):
        recorded_data[j][0] = trial[0]

recorded_data = [r for r in recorded_data if r[0] != -1]
recorded_data.sort(key=cmp_to_key(cmp_row))

# condition, sensor, x, y, z
fmt = "%d, %d, %.18e, %.18e, %.18e"
np.savetxt('data.csv', np.array(recorded_data), fmt=fmt)

print('end')
