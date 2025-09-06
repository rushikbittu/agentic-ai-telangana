import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate


def _iqr_outlier_counts(s: pd.Series):
    s = pd.to_numeric(s, errors="coerce").dropna()
    if s.empty:
        return 0
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return 0
    lower, upper = q1 - 1.5*iqr, q3 + 1.5*iqr
    return int(((s < lower) | (s > upper)).sum())


def generate_insights(transformed_path, config, output_dir):
    df = pd.read_csv(transformed_path)
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    summary_stats = df.describe(include="all").transpose()

    missing = df.isna().sum().rename("missing_count").to_frame()
    missing["missing_pct"] = (missing["missing_count"] / max(len(df), 1) * 100).round(2)

    outliers = []
    for c in numeric_cols:
        outliers.append({"column": c, "iqr_outliers": _iqr_outlier_counts(df[c])})
    outlier_df = pd.DataFrame(outliers) if outliers else pd.DataFrame(columns=["column", "iqr_outliers"])

    categorical_summary = {}
    for c in categorical_cols:
        top_vals = df[c].value_counts(dropna=False).head(5)
        categorical_summary[c] = top_vals
    
    numeric_plot_paths = []
    if numeric_cols:
        plt.figure(figsize=(12, 6))
        df[numeric_cols].hist(bins=20, figsize=(12, 8))
        plot_path = os.path.join(output_dir, "numeric_distributions.png")
        plt.tight_layout()
        plt.savefig(plot_path, dpi=150)
        plt.close()
        numeric_plot_paths.append(plot_path)
    else:
        numeric_plot_paths = []

 
    summary_md = os.path.join(output_dir, "summary.md")
    with open(summary_md, "w", encoding="utf-8") as f:
        f.write("# Dataset Summary & Insights\n\n")

      
        schema_map_path = os.path.join(output_dir, "schema_map.json")
        if os.path.exists(schema_map_path):
            try:
                schema_map = json.load(open(schema_map_path, "r", encoding="utf-8"))
                f.write("## Schema Map (original → standardized)\n\n")
                f.write("| Original | Standardized |\n|---|---|\n")
                for o, s in schema_map.items():
                    f.write(f"| {o} | {s} |\n")
                f.write("\n")
            except Exception:
                pass

    
        f.write("## Summary Statistics\n\n")
        try:
            f.write(tabulate(summary_stats, headers="keys", tablefmt="github"))
        except Exception:
            f.write("Could not render summary statistics.\n")
        f.write("\n\n")

        f.write("## Missing Values\n\n")
        f.write(missing.to_markdown())
        f.write("\n\n")

        if not outlier_df.empty:
            f.write("## Outlier Counts (IQR method)\n\n")
            f.write(outlier_df.to_markdown(index=False))
            f.write("\n\n")

        if categorical_summary:
            f.write("## Categorical Columns Value Counts (Top 5)\n\n")
            for c, counts in categorical_summary.items():
                f.write(f"### Column: {c}\n\n")
                f.write(counts.to_frame(name="count").to_markdown())
                f.write("\n\n")

        if numeric_plot_paths:
            f.write(f"**Numeric distributions plot saved:** `{os.path.basename(numeric_plot_paths[0])}`\n")

    return summary_md, numeric_plot_paths
