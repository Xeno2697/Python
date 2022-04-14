#!/usr/bin/env python3
from collections import deque
 
 
def main():
    N, M = map(int, input().split())
    A = []
    S = set()
    #setは順番を持たないList構造
 
    for _ in range(M):
        k = int(input())
        A.append(list(map(int, input().split()))[::-1])
 
    d = deque(range(M))
    dic = dict()
 
    while d:
        i = d.popleft()
        #先頭要素取り出し
        c = A[i].pop()
 
        if c in S:
            if A[i]:
                d.append(i)
            if A[dic[c]]:
                d.append(dic[c])
        else:
            S.add(c)
            dic[c] = i
 
    return "No" if any(A) else "Yes"
 
 
print(main())

##dequeはsort()が使えないがlistよりずっと早い。
##今後は積極的に使用しよう