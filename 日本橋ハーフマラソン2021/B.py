N = int(input())
A = [list(map(int,input().split())) for i in range(N)]
B = [[int(i) for i in range(0)]for j in range(30)]
result = int(0)
#print(A)
for i in range(N):
    for j in range(N):
        a = A[i][j]
        if a!=0:
            B[a-1].append(int(40*i+j))
#print(B)
Can = [[True for i in range(N)]for i in range(N)]
P = [[0 for i in range(N)]for i in range(N)]
for i in range(30):
    for j in B[29-i]:
        x = j//40
        y = j%40
        if Can[x][y]:
            p = (A[x][y]//4)+1 ##パワーの効かせ具合
            P[x][y] = p
            result += p * A[x][y]
            for k in range(x-p,x+p+1):
                for l in range(y-p+abs(x-k),y+p-abs(x-k)+1):
                    if k>=0 and k<N and l>=0 and l <N:
                       Can[k][l]=False
                       #print(k," ",l,"deleated")
            #print(P)
            #print(Can)
#with open('output_B.txt', 'w') as f:
for i in range(N):
    print(*P[i],sep=" ")
        
        #print(*P[i],file=f,sep=" ")
#print(result)