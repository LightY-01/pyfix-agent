from patched_script1 import get_last_element

assert get_last_element([1, 2, 3]) == 3
assert get_last_element([1]) == 1
assert get_last_element([]) == None