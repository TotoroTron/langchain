import unittest
from io import StringIO
import sys

def fibonacci_printer():
    pass  # to be implemented

class TestFibonacciPrinter(unittest.TestCase):
    def setUp(self):
        # Setup to capture printed output
        self.held, sys.stdout = sys.stdout, StringIO()

    def tearDown(self):
        # Close the StringIO and restore normal stdout
        sys.stdout = self.held

    def test_fibonacci_up_to_250(self):
        expected_output = "0\n1\n1\n2\n3\n5\n8\n13\n21\n34\n55\n89\n144\n233\n"
        fibonacci_printer()
        self.assertEqual(sys.stdout.getvalue(), expected_output)