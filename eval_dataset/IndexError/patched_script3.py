def get_tail(items):
    if not items:
        return None
    return items[-1]
print(get_tail([]))