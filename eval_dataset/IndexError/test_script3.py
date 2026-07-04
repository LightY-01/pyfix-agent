from patched_script3 import get_tail

assert get_tail([1, 2, 3]) == 3
assert get_tail([]) == None
assert get_tail([1]) == 1