array = [1,2,4,5,6,7,9,33,56,88,99]

def binary_search(array, target):
    min = 0
    max = len(array)
    guess = max//2
    while min <= max:
        if array[guess] == target:
            return guess
        if array[guess] < target:
            min = guess + 1
        else:
            max = guess - 1
        guess = (min + max)//2
    return -1
print(binary_search(array, 15))
