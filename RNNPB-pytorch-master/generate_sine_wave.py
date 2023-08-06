import math
import csv
import numpy as np
import torch
import matplotlib.pyplot as plt

L = 250
PATH = "C:/Users/kaede/ドキュメント/code/Python/data/"
FILEDATA = ["con01","fl01","car01","cc01","fc01","cac01"]
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

