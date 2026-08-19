import logging
from langchain_core.tools import tool

logger = logging.getLogger("daton.tools.calculator")


@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression. E.g. '2 + 2', 'sqrt(144)', 'sum([1,2,3])'."""
    try:
        allowed_names = {
            "abs": abs, "round": round, "min": min, "max": max,
            "sum": sum, "len": len, "pow": pow,
            "pi": 3.141592653589793, "e": 2.718281828459045,
        }
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        logger.info("Calculator: %s = %s", expression, result)
        return str(result)
    except Exception as e:
        logger.error("Calculator error: %s -> %s", expression, e)
        return f"Calculation error: {str(e)}"
