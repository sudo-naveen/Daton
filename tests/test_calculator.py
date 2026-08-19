import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from backend.tools.calculator_tool import calculator


def test_basic_multiplication():
    result = calculator.invoke({"expression": "125 * 48"})
    assert result == "6000"


def test_percentage_calculation():
    result = calculator.invoke({"expression": "(65000 - 50000) / 50000 * 100"})
    assert result == "30.0"


def test_sum():
    result = calculator.invoke({"expression": "sum([10, 20, 30, 40, 50])"})
    assert result == "150"


def test_division():
    result = calculator.invoke({"expression": "100 / 4"})
    assert result == "25.0"


def test_power():
    result = calculator.invoke({"expression": "pow(2, 10)"})
    assert result == "1024"


def test_invalid_expression():
    result = calculator.invoke({"expression": "import os"})
    assert "error" in result.lower() or "Error" in result
