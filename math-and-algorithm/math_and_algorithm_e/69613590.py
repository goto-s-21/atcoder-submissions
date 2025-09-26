N = int(input())
numbers = list(map(int, input().split()))

ans = sum(numbers) % 100

print(ans)