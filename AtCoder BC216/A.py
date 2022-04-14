import math
X = float(input())
Y = X%1
Y = int(Y*10)
X = int(X//1)
if Y>6:
    print(str(X)+"+")
elif Y<3:
    print(str(X)+"-")
else:
    print(str(X)+"")