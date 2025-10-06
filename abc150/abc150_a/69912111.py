K, X = map(int, input().split())

ans = 500 * K

if ans >= X:
    print("Yes")
    
elif ans < X:
    print("No")