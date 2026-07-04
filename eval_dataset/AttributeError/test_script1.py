from patched_script1 import buy_item

inventory = [1,3,4]
buy_item(inventory, 2)
assert inventory == [1, 3, 4, 2]

inventory = []
buy_item(inventory, 5)
assert inventory == [5]
