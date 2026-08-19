import re
import logging
from langchain_core.tools import tool
import backend.config as config
from backend.database.connection import execute_sql, get_full_schema

logger = logging.getLogger("daton.tools.sql")


def validate_sql(query: str) -> tuple[bool, str]:
    normalized = query.strip().upper()
    for keyword in config.SQL_BLOCKED_KEYWORDS:
        pattern = r'\b' + keyword + r'\b'
        if re.search(pattern, normalized):
            return False, f"Blocked: {keyword} operations are not allowed"
    return True, ""


def _format_results(results: list) -> str:
    if not results:
        return "Query returned no results."

    columns = list(results[0].keys())
    col_widths = {col: max(len(str(col)), max(len(str(row.get(col, ""))) for row in results)) for col in columns}
    col_widths = {col: min(w, 30) for col, w in col_widths.items()}

    header = " | ".join(str(col).ljust(col_widths[col]) for col in columns)
    separator = "-+-".join("-" * col_widths[col] for col in columns)
    rows = []
    for row in results:
        row_str = " | ".join(str(row.get(col, "")).ljust(col_widths[col]) for col in columns)
        rows.append(row_str)

    return f"{header}\n{separator}\n" + "\n".join(rows)


@tool
def sql_tool(query: str) -> str:
    """Run a read-only SQL query. Returns tabular results. Only SELECT allowed."""
    valid, msg = validate_sql(query)
    if not valid:
        return f"Error: {msg}"

    try:
        logger.info("Executing SQL: %s", query)
        results = execute_sql(query)
        if not results:
            return "Query executed successfully but returned no results."

        if len(results) > 50:
            formatted = _format_results(results[:50])
            return f"{formatted}\n\n... ({len(results)} total rows, showing first 50)"

        return _format_results(results)
    except Exception as e:
        logger.error("SQL execution failed: %s", e)
        return f"SQL Error: {str(e)}"


@tool
def get_database_schema() -> str:
    """List all tables and columns in the database. Call before writing SQL queries."""
    try:
        schema = get_full_schema()
        if not schema:
            return "No tables found in the database."
        filtered = {k: v for k, v in schema.items() if not k.startswith("sqlite_")}
        if not filtered:
            return "No user tables found in the database."
        parts = []
        for table, info in filtered.items():
            cols = ", ".join([f"{c['name']} ({c['type']})" for c in info["columns"]])
            parts.append(f"Table: {table}\n  Columns: {cols}")
        return "\n\n".join(parts)
    except Exception as e:
        logger.error("Schema retrieval failed: %s", e)
        return f"Error getting schema: {str(e)}"
