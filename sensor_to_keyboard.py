import numpy as np
import time
import socket
from scipy.stats import kurtosis as sc_kurtosis
from scipy.stats import skew
from scipy import signal
from keras.models import Sequential
from pynput.keyboard import Key, Controller
import decodification


def print_c(val):
    print('\033[93m' + str(val) + '\033[0m')


def press(key):
    keyboard.press(key)
    keyboard.release(key)


movement = {0: "RotateLeft",
            1: "RotateRight",
            2: "ShakeHorizontally",
            3: "ShakeVertically", }
decodification.verbose = False
keyboard = Controller()

# Socket configuration
UDP_IP = '192.168.1.104'
UDP_PORT = 8081
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(0.001)

# Processing parameters
fs = 500                      # Sampling rate
win_length = 0.5               # Window length in seconds
win_samps = int(fs*win_length)  # Number of samples per window


training_data = np.genfromtxt('training_data.csv').tolist()

# Accelerometer = sensor 1
training_data = [r for r in training_data if r[1] == 0]

print_c("Training Classifier")
clfs = decodification.train_clfs(training_data)
print_c("Classifier trained!")


print_c("You can now start the game")
time.sleep(15)
print_c("Starting reading from sensors")
print_c("Start shaking your device :)")
data_buffer = []

start_time = time.time()
start_time2 = start_time
update_time = 0.5
while True:

    try:
        # Read data from UDP connection
        data, addr = sock.recvfrom(1024*1024)

        # Decode binary stream.
        data_string = data.decode('ascii').split(",")

        # Append new sensor data
        nsensors = (len(data_string)-1)/4

        for ind in range(1, len(data_string), 4):
            type = int(data_string[ind])

            if type == 3:
                data_buffer.append(
                    [float(data_string[ind+1]), float(data_string[ind+2]), float(data_string[ind+3])])

    except socket.timeout:
        pass

    ellapsed_time = time.time() - start_time
    if ellapsed_time > update_time and len(data_buffer) >= win_samps:

        start_time = time.time()

        # Get last window
        win_data = np.array(data_buffer[-win_samps:])
        nsignals = win_data.shape[1]

        dataX = np.array(list(map(lambda d: d[0], win_data)))
        dataY = np.array(list(map(lambda d: d[1], win_data)))
        dataZ = np.array(list(map(lambda d: d[2], win_data)))

        features = [np.mean(dataX),
                    np.mean(dataY),
                    np.mean(dataZ),
                    np.std(dataX),
                    np.std(dataY),
                    np.std(dataZ),
                    sc_kurtosis(dataX),
                    sc_kurtosis(dataY),
                    sc_kurtosis(dataZ),
                    skew(dataX),
                    skew(dataY),
                    skew(dataZ)]

        freqsX, psdX = signal.welch(dataX)
        freqsY, psdY = signal.welch(dataY)
        freqsZ, psdZ = signal.welch(dataZ)

        summary_psd = [{}, {}, {}]

        for x in range(len(freqsX)):
            fx = round(freqsX[x] * 100) / 100
            if fx in summary_psd[0]:
                summary_psd[0][fx] =\
                    summary_psd[0][fx] + psdX[x]
            else:
                summary_psd[0][fx] = psdX[x]

        for y in range(len(freqsY)):
            fy = round(freqsY[y] * 100) / 100
            if fy in summary_psd[1]:
                summary_psd[1][fy] =\
                    summary_psd[1][fy] + psdY[y]
            else:
                summary_psd[1][fy] = psdY[y]

        for z in range(len(freqsZ)):
            fz = round(freqsZ[z] * 100) / 100
            if fz in summary_psd[2]:
                summary_psd[2][fz] =\
                    summary_psd[2][fz] + psdZ[z]
            else:
                summary_psd[2][fz] = psdZ[z]

        summary_psd_list_x = [summary_psd[0][i]
                              for i in sorted(list(summary_psd[0].keys()))]
        summary_psd_list_y = [summary_psd[1][i]
                              for i in sorted(list(summary_psd[1].keys()))]
        summary_psd_list_z = [summary_psd[2][i]
                              for i in sorted(list(summary_psd[2].keys()))]

        features.extend(summary_psd_list_x +
                        summary_psd_list_y + summary_psd_list_z)

        ans = np.array([0, 0, 0, 0, 0, 0])
        for i, clf in enumerate(clfs):
            if isinstance(clf, Sequential):
                ans[i] = np.argmax(clf.predict([features]), axis=-1)
            else:
                ans[i] = clf.predict([features])
        counts = np.bincount(ans)
        # for i, a in enumerate(ans):
        #     print_c("clfs {}: {}".format(i, movement[a]))
        if ans[0] == 0 or ans[3] == 0:
            print_c("left")
            press(Key.left)
        elif ans[0] == 2 and ans[3] == 2:
            print_c("down")
            press(Key.down)
        elif ans[0] == 1 or ans[4] == 1:
            print_c("right")
            press(Key.right)
        elif ans[0] == 3:
            print_c("up")
            press(Key.up)
