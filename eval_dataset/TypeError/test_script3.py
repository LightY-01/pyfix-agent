from patched_script3 import append_value

assert append_value([1, 2, 3], 4) == [1, 2, 3, 4]
assert append_value([], 1) == [1]
assert append_value([1], 2) == [1, 2]