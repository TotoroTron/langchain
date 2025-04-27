class Evaluator:
    def __init__(self):
        # Define supported operators and their precedence
        self.operators = set('+-*/')
        self.precedence = {'+': 1, '-': 1, '*': 2, '/': 2}

    def evaluate(self, expression: str) -> int:
        # Remove all whitespaces from the expression
        expression = expression.replace(" ", "")
        nums = []  # Stack for numbers
        ops = []   # Stack for operators

        def apply_operator():
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
                nums.append(int(left / right))  # Integer division

        def higher_precedence(op1, op2):
            return self.precedence[op1] >= self.precedence[op2]

        # Traverse the expression
        i = 0
        while i < len(expression):
            if expression[i].isdigit() or (expression[i] == '-' and (i == 0 or expression[i - 1] in "(+*-/")):
                num = 0
                sign = -1 if expression[i] == '-' else 1
                if expression[i] == '-':
                    i += 1
                # Build the whole number
                while i < len(expression) and expression[i].isdigit():
                    num = num * 10 + int(expression[i])
                    i += 1
                nums.append(sign * num)
                i -= 1
            elif expression[i] == '(':  # Beginning of a subexpression
                ops.append(expression[i])
            elif expression[i] == ')':  # End of subexpression, solve till matching '('
                while ops and ops[-1] != '(':  # Ensure '=' ops to avoid excess evaluation
                    apply_operator()
                ops.pop()  # Pop the matching '('
            elif expression[i] in self.operators:
                # If operator at top has greater precedence, apply it first.
                while (ops and ops[-1] in self.operators and
                       higher_precedence(ops[-1], expression[i])):
                    apply_operator()
                ops.append(expression[i])
            else:
                raise ValueError("Invalid character")
            i += 1

        # Evaluate any remaining expressions
        while ops:
            apply_operator()

        return nums[0]


def evaluate(expression: str) -> int:
    evaluator = Evaluator()
    return evaluator.evaluate(expression)


# Testing within the code
if __name__ == "__main__":
    import unittest

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

    unittest.main()


