import math
import csv
import numpy as np
import torch
import matplotlib.pyplot as plt

L = 250
PATH = "C:/Users/kaede/ドキュメント/code/Python/data/"
FILEDATA = ["con01","con02","con03","con04","con05",
            "fl01","fl02","fl03","fl04","fl05",
            "car01","car02","car03","car04","car05",
            "cc01","cc02","cc03","cc04","cc05",
            "fc01","fc02","fc03","fc04","fc05",
            "cac01","cac02","cac03","cac04","cac05"]
N = len(FILEDATA)

data = np.empty((N, 6, L), 'float64')
for i in range(N):
    with open(PATH+FILEDATA[i]+".csv") as f:
        reader = csv.reader(f)
        c = [row[1:7] for row in reader]
        data[i,:,:] = np.array(c).T

plt.plot(range(L),data[0,0,:],'r')
plt.plot(range(L),data[0,1,:],'g')
plt.plot(range(L),data[0,2,:],'b')
plt.show()

torch.save(data, open('traindata.pt', 'wb'))

