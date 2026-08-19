import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from backend.tools.sql_tool import validate_sql


def test_valid_select():
    valid, msg = validate_sql("SELECT * FROM sales")
    assert valid is True


def test_block_drop():
    valid, msg = validate_sql("DROP TABLE sales")
    assert valid is False
    assert "DROP" in msg


def test_block_delete():
    valid, msg = validate_sql("DELETE FROM sales WHERE id = 1")
    assert valid is False
    assert "DELETE" in msg


def test_block_truncate():
    valid, msg = validate_sql("TRUNCATE TABLE sales")
    assert valid is False


def test_block_update():
    valid, msg = validate_sql("UPDATE sales SET revenue = 0")
    assert valid is False


def test_block_insert():
    valid, msg = validate_sql("INSERT INTO sales VALUES (1, 'test')")
    assert valid is False


def test_block_alter():
    valid, msg = validate_sql("ALTER TABLE sales ADD COLUMN test TEXT")
    assert valid is False


def test_block_create():
    valid, msg = validate_sql("CREATE TABLE evil (id INT)")
    assert valid is False


def test_complex_select():
    valid, msg = validate_sql("SELECT product_name, SUM(revenue) FROM sales GROUP BY product_name ORDER BY SUM(revenue) DESC LIMIT 5")
    assert valid is True
