def sum_array_elements(arr):
    total = 0
    for i in range(len(arr) + 1):
        total += arr[i]
    return total


arr = [10, 20, 30, 40]
print(sum_array_elements(arr))
