"""Safe arithmetic calculator tool.

Uses an AST whitelist instead of `eval`/`exec` so it cannot execute arbitrary
Python code, even if the model is ever tricked into passing something
malicious as the "expression".
"""
import ast
import operator as op

from langchain_core.tools import tool

from utils.logger import get_logger

logger = get_logger(__name__)

_ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.FloorDiv: op.floordiv,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}


def _eval_node(node: ast.AST):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_eval_node(node.operand))
    raise ValueError(f"Unsupported expression component: {ast.dump(node)}")


def safe_eval(expression: str) -> float:
    tree = ast.parse(expression, mode="eval")
    return _eval_node(tree.body)


@tool
def calculator_tool(expression: str) -> str:
    """Evaluate a basic arithmetic expression, e.g. '(42 * 7) / 3 + 2 ** 5'.
    Supports +, -, *, /, //, %, ** and parentheses. Use this instead of doing
    mental math for any numeric computation."""
    logger.debug("calculator_tool called with expression=%r", expression)
    try:
        result = safe_eval(expression)
        return str(result)
    except Exception as exc:
        return f"Could not evaluate expression: {exc}"
