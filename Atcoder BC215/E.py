def fanc (Map,pos,T,point,N):
    #print(Map[pos],end="")
    i = Map[pos]
    if N-1==pos:
        #print(".",end="")
        point = point+1
        if not T[i]:
            point = point+1
            #print(".",end="")
    else:
        if not T[Map[pos+1]]:
            if(Map[pos+1] == i):
                point = fanc(Map,pos+1,T,point,N)
            else:
                T[i]=True
                point = fanc(Map,pos+1,T,point,N)
                T[i]=False
        point += fanc(Map,pos+1,T,point,N)-point
    return point


N = int(input())
S = str(input())
Map = list()
for i in range(N):
        Map.append(ord(S[i])-65)
Gone = [False]*10
#print(Map)
result = fanc(Map,0,Gone,0,N)
print((result+1)%998244353)