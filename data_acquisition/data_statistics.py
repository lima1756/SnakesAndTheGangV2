import numpy as np
from scipy.stats import kurtosis as sc_kurtosis
from scipy.stats import skew
from scipy import signal
import matplotlib.pyplot as plt

# Step 2, getting all the statistics for each window, sensor, movement.
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

psd = [[[], [], []],
                  [[], [], []],
                  [[], [], []],
                  [[], [], []]]

summary_psd = [[[], [], []],
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
        number_of_windows = len(data_as_matrix[movement[m]][sensor[s]])

        for window in range(number_of_windows):
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

            # print("Movement: " + m + " Sensor: " + s + " Window: " + str(window))
            # print("\tAverage: " + str(average[movement[m]][sensor[s]][window]))
            # print("\tStandard Deviation: " + str(standard_deviation[movement[m]][sensor[s]][window]))
            # print("\tKurtosis: " + str(kurtosis[movement[m]][sensor[s]][window]))
            # print("\tSkewness: " + str(skewness[movement[m]][sensor[s]][window]))

            # Step 4
            # Calculate PSD for each window.

            freqsX, psdX = signal.welch(dataX)
            freqsY, psdY = signal.welch(dataY)
            freqsZ, psdZ = signal.welch(dataZ)

            if not summary_psd[movement[m]][sensor[s]]:
                summary_psd[movement[m]][sensor[s]].extend([{}, {}, {}])

            for x in range(len(freqsX)):
                fx = round(freqsX[x] * 100) / 100
                if fx in summary_psd[movement[m]][sensor[s]][0]:
                    summary_psd[movement[m]][sensor[s]][0][fx] =\
                        summary_psd[movement[m]][sensor[s]][0][fx] + psdX[x]
                else:
                    summary_psd[movement[m]][sensor[s]][0][fx] = psdX[x]

            for y in range(len(freqsY)):
                fy = round(freqsY[y] * 100) / 100
                if fy in summary_psd[movement[m]][sensor[s]][1]:
                    summary_psd[movement[m]][sensor[s]][1][fy] =\
                        summary_psd[movement[m]][sensor[s]][1][fy] + psdY[y]
                else:
                    summary_psd[movement[m]][sensor[s]][1][fy] = psdY[y]

            for z in range(len(freqsZ)):
                fz = round(freqsZ[z] * 100) / 100
                if fz in summary_psd[movement[m]][sensor[s]][2]:
                    summary_psd[movement[m]][sensor[s]][2][fz] =\
                        summary_psd[movement[m]][sensor[s]][2][fz] + psdZ[z]
                else:
                    summary_psd[movement[m]][sensor[s]][2][fz] = psdZ[z]

            psd[movement[m]][sensor[s]].append([[freqsX, psdX],
                                                [freqsY, psdY],
                                                [freqsZ, psdZ]])

        for i in range(len(summary_psd[movement[m]][sensor[s]])):
            for f in summary_psd[movement[m]][sensor[s]][i]:
                summary_psd[movement[m]][sensor[s]][i][f] = summary_psd[movement[m]][sensor[s]][i][f] / number_of_windows

        # print("Movement: " + m + " Sensor: " + s )
        # print("\tpsd: " + str(summary_psd[movement[m]][sensor[s]]))

        # Step 5: Plot PSD for each Sensor - Movement

        # plotting the line 1 points
        plt.plot([k for k in summary_psd[movement[m]][sensor[s]][0]],
                 [summary_psd[movement[m]][sensor[s]][0][k] for k in summary_psd[movement[m]][sensor[s]][0]],
                 label="Frecuencies on x")
        # plotting the line 2 points
        plt.plot([k for k in summary_psd[movement[m]][sensor[s]][1]],
                 [summary_psd[movement[m]][sensor[s]][1][k] for k in summary_psd[movement[m]][sensor[s]][1]],
                 label="Frecuencies on y")
        # plotting the line 2 points
        plt.plot([k for k in summary_psd[movement[m]][sensor[s]][2]],
                 [summary_psd[movement[m]][sensor[s]][2][k] for k in summary_psd[movement[m]][sensor[s]][2]],
                 label="Frecuencies on z")
        plt.xlabel('Frecuency')
        # Set the y axis label of the current axis.
        plt.ylabel('Average Amplitude')
        # Set a title of the current axes.
        plt.title('PSD for' + "Movement: " + m + " Sensor: " + s )
        # show a legend on the plot
        plt.legend()
        # Display a figure.
        plt.show()
