N, M=map(int, input().split())
MAX = 10**5
X = [False]*(MAX+1)
for i in map(int,input().split()):
    X[i] =True
Y = [True]*(M+1)
for i in range(2,MAX+1,1):
    for j in range(i,MAX+1,i):
        if not X[j]:
            continue
        for j in range(i,M+1,i):Y[j]=False
        break
ans = [i for i in range(1,M+1) if Y[i]]
print(len(ans))
print(*ans,sep="\n")

N, M = map(int, input().split())
 
MAX = 10**5
X = [False] * (MAX+1)
for a in map(int, input().split()): X[a] = True
 
Y = [True] * (M+1)
for p in range(2, MAX+1):
    for kp in range(p, MAX+1, p):
        if not X[kp]: continue
        for kp in range(p, M+1, p): Y[kp] = False
        break
 
ans = [i for i in range(1, M+1) if Y[i]]
print(len(ans))
print(*ans,sep='\n')