N,K = map(int,input().split())
S = str(input())
C = [int()]*0
result = [int()]*0
for i in range(len(S)):
    C.append(ord(S[i]))
#print(C)
d = N-K
I = int()
f = int(0)
lenC = len(C)
corcol = 0
while f < K:
    c = 200
    if lenC - corcol <=d:
        d = lenC - corcol -1
    for i in range(d+1):
        if c>C[i+corcol]:
            c=C[i+corcol]
            I = i
    d -= I
    result.append(C[I + corcol])
    f += 1
    corcol += I + 1
    #print(C)
    #print(result)
    #print(str(C[K:]))
for i in range(len(result)):
    print(chr(result[i]),end="")
#for i in range(len(C)):
    #print(chr(C[i]),end="")
print("")