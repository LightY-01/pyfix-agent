n1 = 'David'
n2 = 'Smith'

def format_greeting(first_name, last_name):
    full_name = first_name + ' ' + last_name
    return f'Hello, {full_name}!'
print(format_greeting(n1, n2))