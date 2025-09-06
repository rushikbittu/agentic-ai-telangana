import os
import json
import pandas as pd

def _is_percent_col(colname: str) -> bool:
    
    c = colname.lower()
    return '%' in c or 'percent' in c

def standardize_data(raw_path, output_dir):
    df = pd.read_csv(raw_path)

    original_cols = list(df.columns)
    std_cols = [c.strip().lower().replace(" ", "_") for c in original_cols]
    schema_map = {orig: std for orig, std in zip(original_cols, std_cols)}
    df.columns = std_cols

    parsed_dates = []
    for col in df.columns:
        if "date" in col:

            s = pd.to_datetime(df[col], errors="coerce")
            if s.notna().any():
                df[col] = s
                df[f"{col}_yyyy_mm"] = s.dt.to_period("M").astype(str)
                parsed_dates.append(col)

    coerced_percent = []
    for col in df.columns:
        if _is_percent_col(col):
            df[col] = pd.to_numeric(df[col], errors="coerce")
            coerced_percent.append(col)

    std_path = os.path.join(output_dir, "standardized.csv")
    df.to_csv(std_path, index=False)

    with open(os.path.join(output_dir, "schema_map.json"), "w", encoding="utf-8") as f:
        json.dump(schema_map, f, ensure_ascii=False, indent=2)

    summary_path = os.path.join(output_dir, "02_standardization_summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("# Standardization Summary\n\n")
        f.write("## Column Mapping (original → standardized)\n\n")
        f.write("| Original | Standardized |\n|---|---|\n")
        for o, s in schema_map.items():
            f.write(f"| {o} | {s} |\n")
        f.write("\n")

        f.write("## Dtypes after standardization\n\n")
        dtypes = pd.read_csv(std_path, nrows=0).dtypes  
        dtypes = df.dtypes
        f.write("| Column | Dtype |\n|---|---|\n")
        for c, t in dtypes.items():
            f.write(f"| {c} | {t} |\n")
        f.write("\n")

        if parsed_dates:
            f.write(f"- **Parsed date columns:** {', '.join(parsed_dates)}\n")
            f.write("- Added corresponding `YYYY-MM` helper columns.\n")
        if coerced_percent:
            f.write(f"- **Percent-like columns coerced to float:** {', '.join(coerced_percent)}\n")

    return std_path
