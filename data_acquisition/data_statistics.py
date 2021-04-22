import numpy as np
from scipy.stats import kurtosis as sc_kurtosis
from scipy.stats import skew


def to_string(ar):
    stri = ""
    for i in ar:
        stri = stri + str(np.around(i,3)) + ", "
    return stri


data_as_matrix = [[[], [], []],
                  [[], [], []],
                  [[], [], []],
                  [[], [], []]]

average = [[[], [], []],
                  [[], [], []],
                  [[], [], []],
                  [[], [], []]]

standard_deviation = [[[], [], []],
                  [[], [], []],
                  [[], [], []],
                  [[], [], []]]

kurtosis = [[[], [], []],
                  [[], [], []],
                  [[], [], []],
                  [[], [], []]]

skewness = [[[], [], []],
                  [[], [], []],
                  [[], [], []],
                  [[], [], []]]

sensor = {"ACCELEROMETER": 0,
          "GYROSCOPIC": 1,
          "MAGNETIC_SENSOR": 2}

movement = {"RotateLeft": 0,
            "RotateRight": 1,
            "ShakeHorizontally": 2,
            "ShakeVertically": 3,}

with open("./data.csv") as file:
    for line in file:
        stripped_line = line.strip()
        arr = stripped_line.split(", ")
        data_as_matrix[int(arr[0]) - 1][int(arr[1])-3].append(list(map(float, arr[2:])))

for m in movement:
    for s in sensor:
        dataSensorMov = data_as_matrix[movement[m]][sensor[s]]

        dataX = np.array(list(map(lambda d: d[0], dataSensorMov)))
        dataY = np.array(list(map(lambda d: d[1], dataSensorMov)))
        dataZ = np.array(list(map(lambda d: d[2], dataSensorMov)))

        average[movement[m]][sensor[s]].extend([np.mean(dataX),
                   np.mean(dataY),
                   np.mean(dataZ)])
        standard_deviation[movement[m]][sensor[s]].extend([ np.std(dataX),
                               np.std(dataY),
                               np.std(dataZ)])

        kurtosis[movement[m]][sensor[s]].extend([sc_kurtosis(dataX),
                                                 sc_kurtosis(dataY),
                                                 sc_kurtosis(dataZ)])

        skewness[movement[m]][sensor[s]].extend([skew(dataX),
                                                 skew(dataY),
                                                 skew(dataZ)])

        print("Movement: " + m + " Sensor: " + s)
        print("\tAverage: " + to_string(average[movement[m]][sensor[s]]))
        print("\tStandard Deviation: " + to_string(standard_deviation[movement[m]][sensor[s]]))
        print("\tKurtosis: " + to_string(kurtosis[movement[m]][sensor[s]]))
        print("\tSkewness: " + to_string(skewness[movement[m]][sensor[s]]))

