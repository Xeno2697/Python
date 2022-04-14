N = int(input())
M = [[False for i in range(10**5)]for j in range(10**5)]
result = int(0)
for i in range(N-1):
    u,v,w = map(int,input().split())
    M[u-1][v-1] = w
    M[v-1][u-1] = w
for i in range(0,N-1):
    for j in range(i+1,N):
        #iからjまでの最短経路を捜索
        C = [int(0)]*(10**5)
        D = [True]*(10**5)
        C[i]=1
        while C[j]==0:
            Cc = [C[i] for i in range(10**5)]
            for k in [n for n in range(10**5) if Cc[n] and D[n]]:
                    for l in [n for n in range(10**5) if not Cc[n] and D[n]]:
                        if (M[k][l]>0):
                            if(C[l]<M[k][l]):
                               C[l]=M[k][l]
                            if(C[l]<Cc[k]):
                               C[l]=Cc[k]
                    D[k]=False
        result+=C[j]
        #print(C)
        #print(i,"から",j,"まで",C[j])
print(result)