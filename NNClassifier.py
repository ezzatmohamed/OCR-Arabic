from sklearn.neural_network import MLPClassifier

from FeatureExtraction import *
from sklearn import svm
# from thundersvm import SVC
import tensorflow as tf
import pickle
import time
import cv2
import numpy as np

def Train(X,Y):
    clf=MLPClassifier(hidden_layer_sizes=(50,40))
    print("Started Training")
    ts = time.perf_counter() * 1000
    X_np=np.array(X)
    y_np=np.array(Y)
    # print(X_np.shape,y_np.shape)
    # print(X_np)
    clf.fit(X_np,y_np)

    te=time.perf_counter()*1000

    print("Ended Training in:",te-ts,"ms")
    return clf

f=open("associtations.txt",'r')
lines = f.readlines()
f.close()

X=[[]]
Y=[]
pics=[]
for line in lines:
    line=line.strip()
    temp=line.split(" ")
    Y.append(int(temp[0]))
    pics.append(temp[1])


file=open("Features.txt",'r')
lines=file.readlines()
# print(len(lines))
line_no = 0
print(len(lines))
for line in lines:
    line=line.strip()
    temp=line.split(" ")
    X.append([])
    for floating_num in temp:
        X[line_no].append(float(floating_num))
    line_no += 1
    # pics.append(temp[1])
del(X[-1])
# print(lines)
# print("l;l",X.shape)

classifier=Train(X,Y)

Clas = open('Classifier', 'wb')

pickle.dump(classifier, Clas)
Clas.close()


