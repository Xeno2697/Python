S, T= map(int,input().split())
result=int(0)
for a in range(S+1):
    for b in range(S-a+1):
        for c in range(S-a-b+1):
           if(a*b*c<=T):result+=1
print(result)