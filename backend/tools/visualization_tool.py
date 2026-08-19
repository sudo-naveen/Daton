import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import json
import os
import uuid
import logging
from typing import Optional
from langchain_core.tools import tool
import backend.config as config

logger = logging.getLogger("daton.tools.viz")


@tool
def create_chart(
    chart_type: str,
    data_json: str,
    title: str = "Chart",
    x_label: str = "",
    y_label: str = "",
    x_column: Optional[str] = None,
    y_column: Optional[str] = None,
) -> str:
    """Create a chart: bar, line, scatter, histogram, pie. data_json is a JSON list of objects or dict of lists. Specify x_column, y_column for axes."""
    fig = None
    try:
        data = json.loads(data_json)

        if isinstance(data, dict):
            df = pd.DataFrame(data)
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            return "Error: data_json must be a JSON array of objects or a JSON object with lists"

        if df.empty:
            return "Error: The provided data is empty"

        fig, ax = plt.subplots(figsize=(10, 6))

        if chart_type == "bar":
            if x_column and y_column and x_column in df.columns and y_column in df.columns:
                ax.bar(df[x_column].astype(str), pd.to_numeric(df[y_column], errors='coerce'))
                plt.xticks(rotation=45, ha='right')
            elif len(df.columns) >= 2:
                ax.bar(df.iloc[:, 0].astype(str), pd.to_numeric(df.iloc[:, 1], errors='coerce'))
                plt.xticks(rotation=45, ha='right')

        elif chart_type == "line":
            if x_column and y_column and x_column in df.columns and y_column in df.columns:
                ax.plot(df[x_column], pd.to_numeric(df[y_column], errors='coerce'), marker='o')
            elif len(df.columns) >= 2:
                ax.plot(df.iloc[:, 0], pd.to_numeric(df.iloc[:, 1], errors='coerce'), marker='o')

        elif chart_type == "scatter":
            if x_column and y_column and x_column in df.columns and y_column in df.columns:
                ax.scatter(df[x_column], pd.to_numeric(df[y_column], errors='coerce'))
            elif len(df.columns) >= 2:
                ax.scatter(df.iloc[:, 0], pd.to_numeric(df.iloc[:, 1], errors='coerce'))

        elif chart_type == "histogram":
            col = y_column if y_column and y_column in df.columns else (df.columns[1] if len(df.columns) > 1 else df.columns[0])
            ax.hist(df[col].dropna(), bins=20, edgecolor='black')

        elif chart_type == "pie":
            if x_column and y_column and x_column in df.columns and y_column in df.columns:
                ax.pie(pd.to_numeric(df[y_column], errors='coerce'), labels=df[x_column].astype(str), autopct='%1.1f%%')
            elif len(df.columns) >= 2:
                ax.pie(pd.to_numeric(df.iloc[:, 1], errors='coerce'), labels=df.iloc[:, 0].astype(str), autopct='%1.1f%%')

        else:
            plt.close(fig)
            return f"Unsupported chart type: {chart_type}. Supported: bar, line, scatter, histogram, pie"

        ax.set_title(title)
        if x_label:
            ax.set_xlabel(x_label)
        if y_label:
            ax.set_ylabel(y_label)

        plt.tight_layout()

        chart_dir = os.path.join(config.DATA_DIR, "charts")
        os.makedirs(chart_dir, exist_ok=True)
        chart_path = os.path.join(chart_dir, f"chart_{uuid.uuid4().hex[:12]}.png")
        fig.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        fig = None

        logger.info("Chart created: %s at %s", title, chart_path)
        return json.dumps({
            "status": "success",
            "chart_path": chart_path,
            "message": f"Chart created: {title}"
        })
    except json.JSONDecodeError as e:
        return f"Chart error: Invalid JSON data - {str(e)}"
    except Exception as e:
        logger.error("Chart creation failed: %s", e)
        return f"Chart error: {str(e)}"
    finally:
        if fig is not None:
            plt.close(fig)
