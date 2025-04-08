"""
This program prints the Fibonacci numbers up to 250.
The Fibonacci sequence is a series of numbers where each number is the sum of the two preceding ones, usually starting with 0 and 1.
"""

def print_fibonacci_up_to_250():
    # Initialize the first two Fibonacci numbers
    a, b = 0, 1
    
    # Print the first Fibonacci number
    print(a)
    
    # Continue generating and printing Fibonacci numbers until the next number exceeds 250
    while b <= 250:
        print(b)
        a, b = b, a + b

# Call the function to print the Fibonacci numbers
print_fibonacci_up_to_250()