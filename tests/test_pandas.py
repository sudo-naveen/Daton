import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
import pandas as pd
from backend.tools.python_tool import analyze_data, _load_dataset

SAMPLE_CSV = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_sales.csv")


@pytest.fixture
def sample_csv():
    return SAMPLE_CSV


def test_load_csv(sample_csv):
    df = _load_dataset(sample_csv)
    assert len(df) > 0
    assert "product_name" in df.columns
    assert "revenue" in df.columns


def test_describe(sample_csv):
    result = analyze_data.invoke({
        "dataset_path": sample_csv,
        "analysis_type": "describe",
    })
    assert "mean" in result.lower() or "std" in result.lower()


def test_head(sample_csv):
    result = analyze_data.invoke({
        "dataset_path": sample_csv,
        "analysis_type": "head",
        "column": "5",
    })
    assert "product_name" in result


def test_mean(sample_csv):
    result = analyze_data.invoke({
        "dataset_path": sample_csv,
        "analysis_type": "mean",
        "column": "revenue",
    })
    assert "Mean" in result


def test_groupby(sample_csv):
    result = analyze_data.invoke({
        "dataset_path": sample_csv,
        "analysis_type": "groupby",
        "group_by": "region",
        "column": "revenue",
    })
    assert "North" in result or "South" in result


def test_missing_values(sample_csv):
    result = analyze_data.invoke({
        "dataset_path": sample_csv,
        "analysis_type": "missing",
    })
    assert isinstance(result, str)


def test_duplicates(sample_csv):
    result = analyze_data.invoke({
        "dataset_path": sample_csv,
        "analysis_type": "duplicates",
    })
    assert "Duplicate" in result


def test_summary(sample_csv):
    result = analyze_data.invoke({
        "dataset_path": sample_csv,
        "analysis_type": "summary",
    })
    assert "Shape" in result


def test_value_counts(sample_csv):
    result = analyze_data.invoke({
        "dataset_path": sample_csv,
        "analysis_type": "value_counts",
        "column": "product_name",
    })
    assert isinstance(result, str)
