class Evaluator:
    def __init__(self):
        self.operators = set('+-*/')
        self.priorities = {'+': 1, '-': 1, '*': 2, '/': 2}

    def evaluate(self, expression: str) -> int:
        nums = []  # stack for numbers
        ops = []   # stack for operators

        def apply_operator():
            right = nums.pop()
            left = nums.pop()
            op = ops.pop()
            result = None
            if op == '+':
                result = left + right
            elif op == '-':
                result = left - right
            elif op == '*':
                result = left * right
            elif op == '/':
                result = int(left / right)  # Integer division truncates toward zero
            nums.append(result)

        def precedence(op1, op2):
            return self.priorities[op1] >= self.priorities[op2]

        i = 0
        while i < len(expression):
            if expression[i] == ' ':
                i += 1
                continue

            if expression[i].isdigit():
                num = 0
                while i < len(expression) and expression[i].isdigit():
                    num = num * 10 + int(expression[i])
                    i += 1
                nums.append(num)
                # Decrement i because last inner while loop also increments i
                i -= 1

            elif expression[i] == '(':
                ops.append(expression[i])
            elif expression[i] == ')':
                while ops and ops[-1] != '(':  # Solve entire bracket
                    apply_operator()
                ops.pop()  # Remove '(' from stack
            elif expression[i] in self.operators:
                # While top of ops has same or greater precedence
                while (ops and ops[-1] in self.operators
                       and precedence(ops[-1], expression[i])):
                    apply_operator()
                ops.append(expression[i])
            i += 1

        # Final reduction of entire expression
        while ops:
            apply_operator()

        return nums[0]

def evaluate(expression: str) -> int:
    evaluator = Evaluator()
    return evaluator.evaluate(expression)