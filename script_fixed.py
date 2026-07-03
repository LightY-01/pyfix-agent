name1 = 'John'
name2 = 'Jane'
mylist = [1, 2, 3]
print(f"Hello, I am {name1}, your name is {name2}, isn't it?")

def parsing():
    import ast
    ast.parse('[1,2,3]')
parsing()
print(mylist[2])