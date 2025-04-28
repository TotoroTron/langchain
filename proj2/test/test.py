# test_calculator.py
import unittest
from solution import evaluate

class TestCalculator(unittest.TestCase):
    
    def test_simple_expression(self):
        # Testing simple expression without whitespace
        self.assertEqual(evaluate("3+2*2"), 7)

    def test_whitespace_variants(self):
        # Testing expression with whitespaces
        self.assertEqual(evaluate(" 3 /2 "), 1)

    def test_nested_parentheses(self):
        # Testing expression with nested parentheses
        self.assertEqual(evaluate("(2+3)*(4-1)"), 15)

    def test_division_with_negatives(self):
        # Testing division with negative numbers, expect truncation towards zero
        self.assertEqual(evaluate("-7/3"), -2)

    def test_deeply_nested_parentheses(self):
        # Testing deeply nested expression
        self.assertEqual(evaluate("((1+2)*((3-4)+5))/2"), 6)

    def test_invalid_syntax(self):
        # Testing invalid syntax, expecting exception
        with self.assertRaises(Exception):
            evaluate("""
            3 + + 2
            """)

if __name__ == '__main__':
    unittest.main()
