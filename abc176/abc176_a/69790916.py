N, X, T = map(int, input().split())

if N % X == 0:
    ans = (N // X) * T
    print(ans)
    
elif N % X >= 1:
    ans = ((N // X) + 1) *T
    print(ans)