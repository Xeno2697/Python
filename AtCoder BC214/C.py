N = int(input())
S = list(map(int,input().split()))
T = list(map(int,input().split()))
timetable = [10**9]*N
for i in range(0,N):
    if timetable[i]>T[i]:
        timetable[i]=T[i]
        t =T[i]
        for j in range(1,N+1):
            k = i+j
            if k>N-1:
                k = k-N
            l = k-1
            if k==0:l=N-1
            #print(k,l)
            if timetable[k]<= t+S[l]:break
            timetable[k]= t+S[l]
            t = timetable[k]
    #print(timetable)
print(*timetable,sep="\n")