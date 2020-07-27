query = [1,2]

for i in range(1, len(query) + 1):
    print(query[:len(query) - i] + query[len(query) + 1 - i:])