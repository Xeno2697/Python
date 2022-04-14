import math
N,M,K = map(int,input().split())
#N=300 M=1000 K=10**8
A = list(map(int,input().split()))
p = int()
q = int()
with open('output.txt', 'w') as f:
 for i in range(M):
    a = int(0)
    b = int(0)
    c = int(K)
    cc = int(0)
    for j in range(N):
        if A[j]>=A[a]:
            a=j
    s=K-A[a]
    b=a
    for r in range(N):
            if A[r]>=s and c>A[r]-s:
                c = A[r]-s
                b = r
    A[a] = (A[a] + A[b])%K
    print(a," ",b)
    print(a," ",b,file=f)
    
result = int(0)

for i in range(N):
    result += math.log2(K)-math.log2(A[i]+1)
print(math.ceil(result))

'''
for i in range(M):
    hyoka = int(10**11)
    
    for j in range(N):
        for k in range(N):
            A_copy = [A[l] for l in range(N)]
            A_copy[j] = (A_copy[j]+A_copy[k])%K
            num = int(0)
            for l in range(N):
                num += A_copy[l]
            if hyoka > num:
                hyoka = num
                #print(num)
                p=j
                q=k
    A[p] = (A[p] + A[q])%K
    print(p," ",q)
#print(A)
'''