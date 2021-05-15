import csv
import numpy as np

sensor = 3

trials1 = [
    [4, 75, 225],
    [3, 375, 525],
    [4, 676, 826],
    [3, 976, 1126],
    [1, 1277, 1427],
    [2, 1577, 1727],
    [1, 1878, 2028],
    [2, 2178, 2328],
    [1, 2479, 2629],
    [3, 2779, 2929],
    [4, 3079, 3229],
    [2, 3380, 3530]
]


trials2 = [
    [1, 75, 225],
    [3, 375, 525],
    [1, 676, 826],
    [2, 976, 1126],
    [4, 1276, 1426],
    [3, 1576, 1727],
    [4, 1877, 2027],
    [1, 2178, 2328],
    [2, 2478, 2628],
    [4, 2778, 2928],
    [4, 3078, 3229],
    [3, 3379, 3529]
]


def read_data_file(file_name, trials):

    with open(file_name) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=' ')
        data = []
        clean_data = []
        for row in csv_reader:
            data.append(row)
        for t in trials:
            curr_data = data[t[1]:t[2]]
            clean_data += [[t[0], 3]+x for x in curr_data]
        return np.array(clean_data).astype(np.float)


fmt = "%d, %d, %.18e, %.18e, %.18e"
data1 = read_data_file('./input_test_data1.csv', trials1)
np.savetxt('processsed_test_data1.csv', np.array(data1), fmt=fmt)
data2 = read_data_file('./input_test_data2.csv', trials2)
np.savetxt('processsed_test_data2.csv', np.array(data2), fmt=fmt)
