from itertools import chain
def sum_for_list(lst):
    def prime_factors(n):
        if n < 0:
            n *= -1
        i = 2
        factors = []
        while i * i <= n:
            if n % i:
                i += 1
            else:
                n //= i
                factors.append(i)
        if n > 1:
            factors.append(n)
        return factors
    T = [(num, prime_factors(num)) for num in lst]
    PFs = sorted(set(chain(*map(prime_factors, lst))))
    return [[pf, sum(t[0] for t in T if pf in t[1])] for pf in PFs]
print(sum_for_list([15, 30, -45]))