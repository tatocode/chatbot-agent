import ast
import operator

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def safe_eval(expr: str):
    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)

        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.BinOp):
            left = visit(node.left)
            right = visit(node.right)
            return OPS[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp):
            return OPS[type(node.op)](visit(node.operand))

        raise ValueError("不支持的表达式")

    tree = ast.parse(expr, mode="eval")
    return visit(tree)

def main() -> None:
    import sys

    args = sys.argv[1:]
    if len(args) == 0:
        print("No formula was passed in.")
        return
    elif len(args) > 1:
        print("Too many formulas were passed in.")
        return
    else:
        formula = args[0]
        try:
            print(safe_eval(formula))
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()