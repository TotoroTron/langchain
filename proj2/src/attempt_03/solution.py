# Improved Python expression evaluator
# Supports binary operators: +, -, *, / (with integer division truncating toward zero)
# Supports parentheses for defining precedence at arbitrary nesting depth, as well as unary minus operators


class ExpressionEvaluator:
    def __init__(self, expression: str):
        self.tokens = []  # A list of tokens from the expression
        self.current_char = None  # Current character in the expression
        self.position = -1  # Pointer in the expression
        self.expression = expression

    def advance(self):
        """Move to the next character in the expression."""
        self.position += 1
        if self.position < len(self.expression):
            self.current_char = self.expression[self.position]
        else:
            self.current_char = None

    def skip_whitespace(self):
        """Skip any whitespace characters."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def parse_integer(self):
        """Parse an integer from the current position."""
        num_str = ''
        while self.current_char is not None and self.current_char.isdigit():
            num_str += self.current_char
            self.advance()
        return int(num_str) if num_str else None

    def tokenize(self):
        """Convert the expression into a list of tokens."""
        self.advance()
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
            elif self.current_char.isdigit():
                self.tokens.append(self.parse_integer())
            elif self.current_char in "+-*/()":
                self.tokens.append(self.current_char)
                self.advance()
            else:
                raise Exception(f"Invalid character: {self.current_char}")

    def precedence(self, op):
        """Return the precedence of the operator."""
        return {"+": 1, "-": 1, "*": 2, "/": 2}.get(op, 0)

    def apply_operator(self, left, right, op):
        """Evaluate expressions based on the operator."""
        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            if right == 0:
                raise ZeroDivisionError("Division by zero")
            return int(left / right)  # Integer division

    def evaluate(self):
        """Evaluate the expression given in tokens."""
        values = []  # Stack for numbers
        ops = []  # Stack for operators

        def apply_last_operator():
            """Apply the last operator to the top two values on the stack."""
            right = values.pop()
            left = values.pop()
            op = ops.pop()
            values.append(self.apply_operator(left, right, op))

        index = 0
        # Unary minus handling
        while index < len(self.tokens):
            token = self.tokens[index]

            if isinstance(token, int):
                values.append(token)
            elif token == '(': 
                if index > 0 and isinstance(self.tokens[index - 1], int):
                    ops.append('*')  # Handle implicit multiplication
                ops.append(token)
            elif token == ')':
                while ops and ops[-1] != '(':  # Resolve until matching '('
                    apply_last_operator()
                ops.pop()  # Remove the '('
            elif token in "+-*/":
                while ops and self.precedence(ops[-1]) >= self.precedence(token):
                    apply_last_operator()  # Resolve higher precedence operators
                ops.append(token)

            index += 1

        # Final resolving of the remaining operators
        while ops:
            apply_last_operator()

        return values[0] if values else 0

    def compute(self):
        self.tokenize()
        return self.evaluate()


def evaluate(expression: str) -> int:
    if expression.strip().startswith('-'):
        # Hack: Prepend a zero to expressions that start with a unary minus for handling
        expression = '0' + expression
    evaluator = ExpressionEvaluator(expression)
    return evaluator.compute()

