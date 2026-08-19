import pandas as pd
import io
import logging
import os
import glob
from typing import Optional
from langchain_core.tools import tool
import backend.config as config

logger = logging.getLogger("daton.tools.python")


def _load_dataset(dataset_path: str) -> pd.DataFrame:
    if not os.path.exists(dataset_path):
        search_patterns = [
            os.path.join(config.DATASETS_DIR, os.path.basename(dataset_path)),
            os.path.join(config.DATA_DIR, os.path.basename(dataset_path)),
        ]
        for pattern in search_patterns:
            if os.path.exists(pattern):
                dataset_path = pattern
                break
        else:
            available = glob.glob(os.path.join(config.DATASETS_DIR, "*.csv")) + \
                        glob.glob(os.path.join(config.DATASETS_DIR, "*.xlsx"))
            if available:
                raise FileNotFoundError(
                    f"File not found: {dataset_path}. Available: {[os.path.basename(f) for f in available]}"
                )
            raise FileNotFoundError(f"File not found: {dataset_path}")

    ext = os.path.splitext(dataset_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(dataset_path)
    elif ext in (".xlsx", ".xls"):
        return pd.read_excel(dataset_path)
    else:
        raise ValueError(f"Unsupported format: {ext}. Use CSV or Excel.")


@tool
def analyze_data(dataset_path: str, analysis_type: str, column: Optional[str] = None, group_by: Optional[str] = None) -> str:
    """Analyze a CSV/Excel dataset. Types: describe, head, info, mean, median, sum, count, groupby, missing, duplicates, correlation, value_counts, summary. Pass dataset filename or full path. Use column= for specific column. Use group_by= for groupby."""
    try:
        df = _load_dataset(dataset_path)

        if analysis_type == "summary":
            parts = [
                f"Shape: {df.shape[0]} rows x {df.shape[1]} columns",
                f"Columns: {', '.join(df.columns)}",
                f"Types:\n{df.dtypes.to_string()}",
                f"Missing:\n{df.isnull().sum().to_string()}",
                f"Duplicates: {df.duplicated().sum()}",
                f"Stats:\n{df.describe().to_string()}",
            ]
            return "\n".join(parts)
        elif analysis_type == "describe":
            return df.describe().to_string()
        elif analysis_type == "head":
            n = int(column) if column else 5
            return df.head(n).to_string()
        elif analysis_type == "info":
            buf = io.StringIO()
            df.info(buf=buf)
            return buf.getvalue() + f"\nShape: {df.shape}"
        elif analysis_type == "mean":
            return f"Mean of {column}: {df[column].mean()}" if column else df.mean(numeric_only=True).to_string()
        elif analysis_type == "median":
            return f"Median of {column}: {df[column].median()}" if column else df.median(numeric_only=True).to_string()
        elif analysis_type == "sum":
            return f"Sum of {column}: {df[column].sum()}" if column else df.sum(numeric_only=True).to_string()
        elif analysis_type == "count":
            return f"Count of {column}: {df[column].count()}" if column else df.count().to_string()
        elif analysis_type == "groupby":
            if not group_by:
                return "Error: group_by required"
            return df.groupby(group_by)[column].agg(["mean", "sum", "count"]).to_string() if column else df.groupby(group_by).agg(["mean", "sum", "count"]).to_string()
        elif analysis_type == "missing":
            missing = df.isnull().sum()
            lines = [f"{c}: {n} ({n/len(df)*100:.1f}%)" for c, n in missing.items() if n > 0]
            return "Missing:\n" + "\n".join(lines) if lines else "No missing values"
        elif analysis_type == "duplicates":
            return f"Duplicates: {df.duplicated().sum()} / {len(df)} rows"
        elif analysis_type == "correlation":
            numeric = df.select_dtypes(include=["number"])
            return numeric.corr()[column].to_string() if column and column in numeric.columns else numeric.corr().to_string()
        elif analysis_type == "value_counts":
            return df[column].value_counts().head(20).to_string() if column else "Error: column required"
        else:
            return f"Unknown type: {analysis_type}. Use: describe, head, info, mean, median, sum, count, groupby, missing, duplicates, correlation, value_counts, summary"
    except Exception as e:
        return f"Error: {str(e)}"
