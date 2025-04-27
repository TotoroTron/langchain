# Implementing the function to print out Fibonacci numbers up to 250
def fibonacci_printer():
    # Starting numbers in the Fibonacci sequence
    a, b = 0, 1
    # Loop until the generated Fibonacci number exceeds 250
    while a <= 250:
        print(a)
        a, b = b, a + b

# Running the function to demonstrate its functionality
fibonacci_printer()