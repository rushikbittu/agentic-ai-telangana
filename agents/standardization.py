import os
import pandas as pd
import re
import json

DATETIME_KEYWORDS = ['date', 'datetime', 'timestamp', 'time', 'dt']


def _is_datetime_col(colname: str) -> bool:
    colname = colname.lower()
    return any(kw in colname for kw in DATETIME_KEYWORDS)


def _detect_datetime_columns(df):
    candidates = []
    for col in df.columns:
        # Name-based heuristic
        if _is_datetime_col(col):
            candidates.append(col)
            continue

        
        non_null_series = df[col].dropna()
        if len(non_null_series) == 0:
            continue
        sample = non_null_series.astype(str).sample(min(20, len(non_null_series)))
        date_match_count = sum(
            bool(re.match(r"\d{1,4}[\/\.\-\s]\d{1,4}[\/\.\-\s]\d{1,4}", x)) for x in sample
        )
        if date_match_count > len(sample) // 2:
            candidates.append(col)
    return candidates


def ingest_file(filepath):
    if filepath.endswith('.csv'):
        
        for delim in [',', '\t', ';', ' ']:
            try:
                df = pd.read_csv(filepath, delimiter=delim)
                if len(df.columns) > 1:
                    return df
            except Exception:
                continue
        raise ValueError("Unable to load CSV with standard delimiters.")
    elif filepath.endswith('.xlsx'):
        return pd.read_excel(filepath)
    else:
        raise ValueError(f"Unsupported file type for ingestion: {filepath}")


def standardize_data(raw_path, output_dir):
    df = ingest_file(raw_path)

  
    original_cols = list(df.columns)
    std_cols = [c.strip().lower().replace(' ', '_') for c in original_cols]
    schema_map = dict(zip(original_cols, std_cols))
    df.columns = std_cols

   
    parsed_dates = []
    for col in _detect_datetime_columns(df):
        s = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
        if s.notna().any():
            df[col] = s
            df[f"{col}_yyyy_mm"] = s.dt.to_period("M").astype(str)
            parsed_dates.append(col)

    std_path = os.path.join(output_dir, "standardized.csv")
    df.to_csv(std_path, index=False)

   
    with open(os.path.join(output_dir, "schema_map.json"), "w", encoding="utf-8") as f:
        json.dump(schema_map, f, ensure_ascii=False, indent=2)


    summary_md_path = os.path.join(output_dir, "02_standardization_summary.md")
    with open(summary_md_path, "w", encoding="utf-8") as f:
        f.write("# Standardization Summary\n\n")
        f.write("## Column Mapping (original → standardized)\n\n")
        f.write("| Original | Standardized |\n|---|---|\n")
        for o, s in schema_map.items():
            f.write(f"| {o} | {s} |\n")
        f.write("\n")

        f.write("## Parsed date/time columns\n")
        if parsed_dates:
            f.write(", ".join(parsed_dates) + "\n")
        else:
            f.write("None found\n")

    return std_path
