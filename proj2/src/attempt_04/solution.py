import unittest

class Evaluator:
    def __init__(self):
        self.operators = set('+-*/')
        # Define operator precedence
        self.precedence = {'+': 1, '-': 1, '*': 2, '/': 2}

    def evaluate(self, expression: str) -> int:
        # Remove any white spaces in the expression
        expression = expression.replace(" ", "")
        nums = []  # stack for numbers
        ops = []   # stack for operators

        def apply_operator():
            """Applies the operator at the top of ops to the top two numbers in nums."""
            right = nums.pop()
            left = nums.pop()
            op = ops.pop()
            if op == '+':
                nums.append(left + right)
            elif op == '-':
                nums.append(left - right)
            elif op == '*':
                nums.append(left * right)
            elif op == '/':
                if right == 0:
                    raise ZeroDivisionError("Division by zero")
                nums.append(int(left / right))  # Integer division truncates towards zero

        def higher_precedence(op1, op2):
            """Checks if op1 has higher or equal precedence than op2."""
            return self.precedence[op1] >= self.precedence[op2]

        # Iterate through the string expression
        i = 0
        while i < len(expression):
            if expression[i].isdigit() or (expression[i] == '-' and (i == 0 or expression[i-1] == '(')):
                # Process a (possibly negative) number
                num = 0
                sign = -1 if (expression[i] == '-') else 1
                if expression[i] == '-':
                    i += 1
                while i < len(expression) and expression[i].isdigit():
                    num = num * 10 + int(expression[i])
                    i += 1
                nums.append(sign * num)
                i -= 1

            elif expression[i] == '(':
                ops.append(expression[i])
            elif expression[i] == ')':
                while ops[-1] != '(':
                    apply_operator()
                ops.pop()  # Remove the '(' from ops
            elif expression[i] in self.operators:
                while (ops and ops[-1] in self.operators and
                       higher_precedence(ops[-1], expression[i])):
                    apply_operator()
                ops.append(expression[i])
            else:
                raise ValueError("Invalid character")

            i += 1

        # Evaluate any remaining operators
        while ops:
            apply_operator()

        return nums[0]

def evaluate(expression: str) -> int:
    evaluator = Evaluator()
    return evaluator.evaluate(expression)

# Unit tests
class TestCalculator(unittest.TestCase):

    def test_simple_expression(self):
        self.assertEqual(evaluate("3+2*2"), 7)

    def test_whitespace_variants(self):
        self.assertEqual(evaluate(" 3 /2 "), 1)

    def test_nested_parentheses(self):
        self.assertEqual(evaluate("(2+3)*(4-1)"), 15)

    def test_division_with_negatives(self):
        self.assertEqual(evaluate("-7/3"), -2)

    def test_deeply_nested(self):
        self.assertEqual(evaluate("((1+2)*((3-4)+5))/2"), 3)

    def test_invalid_syntax(self):
        with self.assertRaises(Exception):
            evaluate("3 + */ 2")

# Run tests
unittest.main(argv=[''], exit=False)