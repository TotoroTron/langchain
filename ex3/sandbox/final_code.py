def fibonacci_up_to(max_value):
    # Initialize the first two Fibonacci numbers
    a, b = 0, 1
    
    # Print the first Fibonacci number
    print(a, end=', ')
    
    # Generate and print Fibonacci numbers up to max_value
    while b <= max_value:
        print(b, end=', ' if b + a <= max_value else '')
        a, b = b, a + b

# Call the function to print Fibonacci numbers up to 250
fibonacci_up_to(250)