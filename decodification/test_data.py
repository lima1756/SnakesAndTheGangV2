import decodification
import numpy as np

data1 = np.genfromtxt('test_statistics1.csv').tolist()
data2 = np.genfromtxt('test_statistics2.csv').tolist()

print("TESTING SET 1")
decodification.train_clfs(data1)
print("TESTING SET 2")
decodification.train_clfs(data2)
