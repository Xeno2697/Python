N = int(input())
A = list()
# print(A)
while N > 1:
    if N%2 == 1:
        A.append(True)
    N=N//2
    A.append(False)
A.append(True)
#print(A)
a=len(A)
#print(a)
for i in range(a):
    if A[a-i-1]:
        print("A",end="")
    else:
        print("B",end="")
print()