import math

N, X, Y = map(int, input().split())

A = N // X
B = N // Y
C = N // math.lcm(X, Y)

ans = A + B - C

print(ans)