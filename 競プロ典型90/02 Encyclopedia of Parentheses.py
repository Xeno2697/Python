def fib(n,A,a,b):
    if a < n//2:
        fib(n,A+"(",a+1,b)
    if b < a:
        fib(n,A+")",a,b+1)
    if n == a+b:
        print(A)

N = int(input())
A = "("
if N%2 == 0:
    fib(N,A,1,0)


