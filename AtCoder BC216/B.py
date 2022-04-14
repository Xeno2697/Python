N = int(input())
S = [[]for _ in range(N)]
T = [[]for _ in range(N)]
c = False
 
for i in range(N):
    s,t = map(str,input().split())
    S[i].append(s)
    T[i].append(t)
 
#print(S)
 
for i in range(N-1):
    for j in range(i+1,N):
        if S[i]==S[j] and T[i]==T[j]:
            print("Yes")
            c = True
            break
    if c:break
 
if not c:
    print("No")