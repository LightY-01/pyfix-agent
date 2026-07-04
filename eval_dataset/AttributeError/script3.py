arr = [4,2,1,3]

def decreasing_order_list(arr):
    sorted_arr = arr.sort()
    sorted_arr.reverse()
    return sorted_arr

print(decreasing_order_list(arr))