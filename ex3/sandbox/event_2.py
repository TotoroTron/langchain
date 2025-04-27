def fibonacci_sequence(limit):
    a, b = 0, 1
    while a < limit:
        print(a)
        a, b = b, a + b

# Call the function with the limit of 250
fibonacci_sequence(250)