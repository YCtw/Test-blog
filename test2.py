def decorator_function(function):
    def processed_function(a,b):
        k = 3*function(a,b)
        return k
    return processed_function



@decorator_function
def add_on(a,b):
    return a+b

print(add_on(3,4))