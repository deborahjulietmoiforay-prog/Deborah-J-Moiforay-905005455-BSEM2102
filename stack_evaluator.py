import sys

SEPARATOR_CHARS = {"-"}
DEFAULT_SEPARATOR = "-----"
OPERATORS = {"+": 1, "-": 1, "*": 2, "/": 2}
PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "u-": 3}


class Stack:
    """A simple LIFO stack backed by a Python list."""

    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._items[-1]

    def is_empty(self):
        return len(self._items) == 0

    def size(self):
        return len(self._items)


def tokenize(expression):
    tokens = []
    i, n = 0, len(expression)
    while i < n:
        ch = expression[i]
        if ch.isspace():
            i += 1
        elif ch.isdigit() or ch == ".":
            j = i
            while j < n and (expression[j].isdigit() or expression[j] == "."):
                j += 1
            text = expression[i:j]
            if text.count(".") > 1 or text == ".":
                raise ValueError(f"Invalid number '{text}'")
            tokens.append(float(text))
            i = j
        elif ch in OPERATORS or ch in "()":
            unary = (
                ch == "-"
                and (not tokens or tokens[-1] == "(" or tokens[-1] in OPERATORS or tokens[-1] == "u-")
            )
            if unary:
                tokens.append(0.0)
                tokens.append("u-")
            else:
                tokens.append(ch)
            i += 1
        else:
            raise ValueError(f"Invalid character '{ch}'")
    return tokens


def apply_operator(operators, values):
    op = operators.pop()
    if values.size() < 2:
        raise ValueError("Malformed expression")
    right = values.pop()
    left = values.pop()
    if op == "+":
        values.push(left + right)
    elif op == "-" or op == "u-":
        values.push(left - right)
    elif op == "*":
        values.push(left * right)
    elif op == "/":
        if right == 0:
            raise ZeroDivisionError("Division by zero")
        values.push(left / right)


def evaluate_expression(expression):
    tokens = tokenize(expression)
    if not tokens:
        raise ValueError("Empty expression")

    values = Stack()
    operators = Stack()
    expect_operand = True

    for token in tokens:
        if isinstance(token, float):
            if not expect_operand:
                raise ValueError("Missing operator")
            values.push(token)
            expect_operand = False
        elif token == "(":
            if not expect_operand:
                raise ValueError("Missing operator before '('")
            operators.push(token)
        elif token == ")":
            if expect_operand:
                raise ValueError("Missing operand before ')'")
            while not operators.is_empty() and operators.peek() != "(":
                apply_operator(operators, values)
            if operators.is_empty():
                raise ValueError("Unbalanced parentheses")
            operators.pop()
        else:
            if token == "u-":
                operators.push(token)
                expect_operand = True
                continue
            if expect_operand:
                raise ValueError(f"Unexpected operator '{token}'")
            while (
                not operators.is_empty()
                and operators.peek() != "("
                and PRECEDENCE[operators.peek()] >= PRECEDENCE[token]
            ):
                apply_operator(operators, values)
            operators.push(token)
            expect_operand = True

    if expect_operand:
        raise ValueError("Expression ends with an operator")

    while not operators.is_empty():
        if operators.peek() == "(":
            raise ValueError("Unbalanced parentheses")
        apply_operator(operators, values)

    if values.size() != 1:
        raise ValueError("Malformed expression")
    return values.pop()


def format_result(value):
    if value == int(value):
        return str(int(value))
    return str(round(value, 6)).rstrip("0").rstrip(".")


def is_separator(line):
    text = line.strip()
    return len(text) >= 3 and all(c in SEPARATOR_CHARS for c in text)


def read_blocks(path):
    blocks, separator = [], None
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if is_separator(line):
                if separator is None:
                    separator = line
            elif line:
                blocks.append(line)
    return blocks, (separator or DEFAULT_SEPARATOR)


def process_file(input_path, output_path):
    expressions, separator = read_blocks(input_path)
    results = []
    for expr in expressions:
        try:
            results.append(format_result(evaluate_expression(expr)))
        except ZeroDivisionError:
            results.append("Error: Division by zero")
        except (ValueError, IndexError) as err:
            results.append(f"Error: {err}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"\n{separator}\n".join(results) + "\n")
    return expressions, results


def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "output.txt"
    try:
        expressions, results = process_file(input_path, output_path)
    except FileNotFoundError:
        print(f"Error: could not find '{input_path}'.")
        sys.exit(1)
    for expr, res in zip(expressions, results):
        print(f"{expr}  =  {res}")
    print(f"\nDone. {len(results)} expression(s) written to '{output_path}'.")


if __name__ == "__main__":
    main()