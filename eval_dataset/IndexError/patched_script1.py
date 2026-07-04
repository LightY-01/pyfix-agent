def get_last_element(arr):
    if len(arr) == 0:
        return None
    return arr[len(arr) - 1]
arr = [1, 2, 3, 4, 5]
print(get_last_element(arr))
print(get_last_element([]))