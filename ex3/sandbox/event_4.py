def print_fibonacci_up_to_250():
    a, b = 0, 1
    while a < 250:
        print(a)
        a, b = b, a + b

print_fibonacci_up_to_250()