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

    # Summary stats 
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    summary_stats = df.describe(include="all").transpose()

    # Missingness table
    missing = df.isna().sum().rename("missing_count").to_frame()
    missing["missing_pct"] = (missing["missing_count"] / max(len(df), 1) * 100).round(2)

    # Outlier counts (IQR) for numeric columns
    outliers = []
    for c in numeric_cols:
        outliers.append({"column": c, "iqr_outliers": _iqr_outlier_counts(df[c])})
    outlier_df = pd.DataFrame(outliers) if outliers else pd.DataFrame(columns=["column", "iqr_outliers"])

    rain_col = next((c for c in df.columns if "rain" in c.lower()), None)
    district_col = next((c for c in df.columns if "district" in c.lower()), None)
    date_col = next((c for c in df.columns if "date" in c.lower()), None)

    top_by_district_md = ""
    overall_avg = None

    if rain_col is not None:
        overall_avg = pd.to_numeric(df[rain_col], errors="coerce").mean()
        if district_col is not None:
            top_by_district = (
                df.groupby(district_col)[rain_col]
                .mean(numeric_only=True)
                .sort_values(ascending=False)
                .head(10)
                .round(2)
            )
            top_by_district_md = top_by_district.to_frame("avg_rain").to_markdown()


    monthly_plot_path = None
    if (date_col is not None) and (rain_col is not None):
        try:
            sdate = pd.to_datetime(df[date_col], errors="coerce")
            series = pd.to_numeric(df[rain_col], errors="coerce")
            ts = pd.DataFrame({"date": sdate, "rain": series}).dropna()
            if not ts.empty:
                monthly = ts.set_index("date").resample("M")["rain"].sum()
                plt.figure(figsize=(10, 5))
                plt.plot(monthly.index, monthly.values)
                plt.title("Monthly Rainfall (sum)")
                plt.xlabel("Month")
                plt.ylabel("Rain")
                monthly_plot_path = os.path.join(output_dir, "plot_monthly_rainfall.png")
                plt.tight_layout()
                plt.savefig(monthly_plot_path, dpi=150)
                plt.close()
        except Exception:
            monthly_plot_path = None
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

        f.write("## Summary Statistics (numeric)\n\n")
        try:
            f.write(tabulate(summary_stats.select_dtypes("number"), headers="keys", tablefmt="github"))
        except Exception:
            f.write("Could not render numeric stats.\n")
        f.write("\n\n")

        f.write("## Missing Values\n\n")
        f.write(missing.to_markdown())
        f.write("\n\n")

        if not outlier_df.empty:
            f.write("## Outlier Counts (IQR method)\n\n")
            f.write(outlier_df.to_markdown(index=False))
            f.write("\n\n")

        if overall_avg is not None:
            f.write(f"## Rainfall Insights\n\n")
            f.write(f"- **Overall average `{rain_col}`:** {round(float(overall_avg), 2)}\n")
            if top_by_district_md:
                f.write("\n**Top districts by average rainfall (top 10):**\n\n")
                f.write(top_by_district_md)
                f.write("\n\n")

        if monthly_plot_path:
            f.write(f"**Monthly rainfall plot saved:** `{os.path.basename(monthly_plot_path)}`\n")

    return summary_md, monthly_plot_path
