import numpy as np
H, W = map(int,input().split())
A = np.array([input().split() for i in range(H)], dtype=np.int64)
X = A.sum(axis=1)
Y = A.sum(axis=0)
B = np.add.outer(X,Y)-A
for a in B.tolist():
    print(*a)