n = [1, 21, 55]
def solution(n):
    n.sort()
    nwd = 1
    for x in range(n[0], 1, -1):
        for num in n:
            print(num, x)
            if (num/x) % 1 != 0:
                break
            elif num == n[-1]:
                nwd = x
                return nwd * len(n)
    return nwd * len(n)
print(solution(n))