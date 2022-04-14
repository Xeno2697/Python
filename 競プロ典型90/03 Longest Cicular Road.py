import copy

def fab(pos,Map,num,chart,point):
    #print("position",pos+1,"point",points,Map)
    result = int(0)
    if not chart[pos] == -1:
        result = point - chart[pos]
    moto = chart[pos]
    chart[pos] = point

    for l in range(num):
        if l in Map[pos]:
            Map[pos].remove(l)
            Map[l].remove(pos)
            p = fab(l,Map,num,chart,point+1)
            if p > result:
                result = p
            Map[pos].append(l)
            Map[l].append(pos)
    chart[pos]=moto
    return result

N = int(input())
A = [[0 for i in range(0)] for j in range(N)]
B = [[0 for i in range(0)] for j in range(N)]
for i in range(N-1):
    a,b = map(int,input().split())
    A[a-1].append(b-1)
    A[b-1].append(a-1)
result = int(0)
#print(A)
for i in range(N-1):
    for j in range(N-i-1):
        if not j+i+1 in A[i]:
            B = copy.deepcopy(A)
            B[i].append(j+i+1)
            B[j+i+1].append(i)
            #print(i+1,"と",i+j+2,"に道を新設"
            C = [-1 for j in range(N)]
            p = fab(0,B,N,C,0)
            if result < p:
                result = p
print(result)

#処理が遅い