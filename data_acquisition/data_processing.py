import numpy as np
from scipy.stats import kurtosis as sc_kurtosis
from scipy.stats import skew

conditions = [('Rotate left', 1), ('Rotate right', 2),
              ('Shake horizontal', 3), ('Shake vertically', 4)]
time = 40
partioning = 0.25
rate = time/partioning


def to_string(ar):
    stri = ""
    for i in ar:
        stri = stri + str(np.around(i,3)) + ", "
    return stri


data = np.genfromtxt('data.csv', delimiter=',').tolist()


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

for mov in range(4):
    data_as_matrix[mov][sensor["ACCELEROMETER"]] = np.array_split(
        [r[2:] for r in data if r[1] - 3 == sensor["ACCELEROMETER"] and r[0] == mov+1], rate)
    data_as_matrix[mov][sensor["GYROSCOPIC"]] = np.array_split(
        [r[2:] for r in data if r[1]- 3 == sensor["GYROSCOPIC"] and r[0] == mov+1], rate)
    data_as_matrix[mov][sensor["MAGNETIC_SENSOR"]] = np.array_split(
        [r[2:] for r in data if r[1]- 3 == sensor["MAGNETIC_SENSOR"] and r[0] == mov+1], rate)



for m in movement:
    for s in sensor:
        for window in range(len(data_as_matrix[movement[m]][sensor[s]])):
            dataSensorMov = data_as_matrix[movement[m]][sensor[s]][window]

            dataX = np.array(list(map(lambda d: d[0], dataSensorMov)))
            dataY = np.array(list(map(lambda d: d[1], dataSensorMov)))
            dataZ = np.array(list(map(lambda d: d[2], dataSensorMov)))

            average[movement[m]][sensor[s]].extend([np.mean(dataX),
                       np.mean(dataY),
                       np.mean(dataZ)])
            standard_deviation[movement[m]][sensor[s]].append([ np.std(dataX),
                                   np.std(dataY),
                                   np.std(dataZ)])

            kurtosis[movement[m]][sensor[s]].append([sc_kurtosis(dataX),
                                                     sc_kurtosis(dataY),
                                                     sc_kurtosis(dataZ)])

            skewness[movement[m]][sensor[s]].append([skew(dataX),
                                                     skew(dataY),
                                                     skew(dataZ)])

            print("Movement: " + m + " Sensor: " + s + " Window: " + str(window))
            print("\tAverage: " + str(average[movement[m]][sensor[s]][window]))
            print("\tStandard Deviation: " + str(standard_deviation[movement[m]][sensor[s]][window]))
            print("\tKurtosis: " + str(kurtosis[movement[m]][sensor[s]][window]))
            print("\tSkewness: " + str(skewness[movement[m]][sensor[s]][window]))

"""print(len(data_as_matrix))
print(len(data_as_matrix[0]))
print(len(data_as_matrix[0][0]))
print(len(data_as_matrix[0][0][0]))
"""
