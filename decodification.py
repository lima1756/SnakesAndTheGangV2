import numpy as np
from numpy.lib.arraysetops import isin
from sklearn import datasets
from sklearn import svm
from sklearn.model_selection import KFold
from sklearn.metrics import confusion_matrix
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

from keras.models import Sequential
from keras.layers import Dense
from keras.utils import np_utils


# GENERAL VARAIBLES
np.seterr(all='raise')
n_splits = 5
verbose = True


# Import data
sensor = ["ACCELEROMETER", "GYROSCOPIC"]

movement = {0: "RotateLeft",
            1: "RotateRight",
            2: "ShakeHorizontally",
            3: "ShakeVertically", }


def train_clfs(data):
    y = np.array([int(x[0]) for x in data])
    x = np.array([(x[2:]) for x in data])
    n_features = len(x[0])

    kf = KFold(n_splits=n_splits, shuffle=True)
    # classifiers
    clfs = [
        svm.SVC(kernel='linear'),  # 0 - svm_linear
        svm.SVC(kernel='rbf'),  # 1 - svm_rbf
        KNeighborsClassifier(n_neighbors=3),  # 2 - knn
        DecisionTreeClassifier(random_state=0),  # 3 - decision_tree
        Sequential(),  # 4 - singlelayer_perceptron
        Sequential()]  # 5 - multilayer_perceptron

    clfs_names = ["SVC Linear", "SVC RBF", "K Neighbors",
                  "Decision Tree", "Single layer perceptron",
                  "Multilayer perceptron"]

    clfs[4].add(
        Dense(4, input_dim=n_features, activation='softmax'))

    clfs[5].add(Dense(64, input_dim=n_features, activation='relu'))
    clfs[5].add(Dense(32, activation='relu'))
    clfs[5].add(Dense(16, activation='relu'))
    clfs[5].add(Dense(4, activation='softmax'))

    for i, clf in enumerate(clfs):
        if verbose:
            print("\tClassifier: " + clfs_names[i])
        acc = 0
        prec = [0 for i in movement]
        recall = [0 for i in movement]
        for train_index, test_index in kf.split(x):

            # Training phase
            x_train = x[train_index, :]
            y_train = y[train_index]
            if isinstance(clf, Sequential):
                y_train = np_utils.to_categorical(y_train)
                clf.compile(loss='categorical_crossentropy', optimizer='adam')
                clf.fit(x_train, y_train, epochs=150, batch_size=5, verbose=0)
            else:
                clf.fit(x_train, y_train)

            # Test phase
            x_test = x[test_index, :]
            y_test = y[test_index]
            if isinstance(clf, Sequential):
                y_pred = np.argmax(clf.predict(x_test), axis=-1)
            else:
                y_pred = clf.predict(x_test)

            # Calculate confusion matrix and model performance
            cm = confusion_matrix(y_test, y_pred)
            Tp = 0
            for i in range(len(cm)):
                Tp += cm[i, i]
            acc_i = Tp/len(y_test)
            for i in range(len(cm)):
                Fn = 0
                Fp = 0
                Tp = cm[i, i]
                for j in range(len(cm)):
                    if(j != i):
                        Fn += cm[i, j]
                        Fp += cm[j, i]
                if Tp != 0:
                    prec[i] += Tp/(Tp+Fp)
                    recall[i] += Tp/(Tp+Fn)
            acc += acc_i

        acc = acc/n_splits
        prec = np.array(prec)/n_splits
        recall = np.array(recall)/n_splits
        if verbose:
            print('\t\tACC = ', acc)
            print('\t\tPRECISION = ', prec)
            print('\t\tRECALL = ', recall)
    return clfs


if __name__ == "__main__":
    data = np.genfromtxt('all_data_statistics.csv').tolist()
    data_per_sensor = []
    for i, s in enumerate(sensor):
        curr_data = [r for r in data if r[1] == i]
        data_per_sensor.append(curr_data)
    for data in data_per_sensor:
        curr_sensor = data[0][1]
        if verbose:
            print("TESTING SENSOR: " + sensor[int(curr_sensor)])
        train_clfs(data)
