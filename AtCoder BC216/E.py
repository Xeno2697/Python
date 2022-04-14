from collections import deque


N,K = map(int,(input().split()))
dic = dict()
ma = int(0)
result = int(0)
A = deque(map(int,input().split()))
for i in range(N):
    n = A.popleft()
    dic[n] = 1 + dic.pop(i,0)
    if n>ma:ma=n
#print(dic)
m = int(0)
while K and max:
    m += dic.pop(ma,0)
    max_d = int(max(dic))
    d = ma-max_d
    if K>m*d:
        result += m*d*max_d+(sum(range(d)))
        K-=m*d
        ma=max_d
    else:
        result += K*ma
        break
print(result)