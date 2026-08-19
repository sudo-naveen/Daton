import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from backend.tools.visualization_tool import create_chart
import json


def test_bar_chart():
    data = json.dumps({"Category": ["A", "B", "C"], "Value": [10, 20, 30]})
    result = create_chart.invoke({
        "chart_type": "bar",
        "data_json": data,
        "title": "Test Bar Chart",
        "x_column": "Category",
        "y_column": "Value",
    })
    parsed = json.loads(result)
    assert parsed["status"] == "success"
    assert os.path.exists(parsed["chart_path"])
    os.remove(parsed["chart_path"])


def test_line_chart():
    data = json.dumps({"Month": ["Jan", "Feb", "Mar"], "Sales": [100, 150, 130]})
    result = create_chart.invoke({
        "chart_type": "line",
        "data_json": data,
        "title": "Test Line Chart",
        "x_column": "Month",
        "y_column": "Sales",
    })
    parsed = json.loads(result)
    assert parsed["status"] == "success"
    os.remove(parsed["chart_path"])


def test_pie_chart():
    data = json.dumps({"Product": ["A", "B", "C"], "Revenue": [40, 35, 25]})
    result = create_chart.invoke({
        "chart_type": "pie",
        "data_json": data,
        "title": "Test Pie Chart",
        "x_column": "Product",
        "y_column": "Revenue",
    })
    parsed = json.loads(result)
    assert parsed["status"] == "success"
    os.remove(parsed["chart_path"])


def test_unsupported_chart():
    data = json.dumps({"A": [1, 2], "B": [3, 4]})
    result = create_chart.invoke({
        "chart_type": "3d_surface",
        "data_json": data,
        "title": "Test",
    })
    assert "error" in result.lower() or "Unsupported" in result
