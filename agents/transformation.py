import os
import json
import pandas as pd

def transform_data(clean_path, config, output_dir):
    df = pd.read_csv(clean_path)

    rows_before = len(df)
    filters = config.get("scope", {}).get("filters", {}) or {}

    for col, val in filters.items():
        if col in df.columns:
            df = df[df[col].astype(str).str.lower() == str(val).lower()]

    rows_after = len(df)
    transformed_path = os.path.join(output_dir, "transformed.csv")
    df.to_csv(transformed_path, index=False)

    summary_path = os.path.join(output_dir, "04_transformation_summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("# Transformation Summary\n\n")
        f.write(f"- **Rows before:** {rows_before}\n")
        f.write(f"- **Rows after:** {rows_after}\n")
        f.write(f"- **Filters applied:** `{json.dumps(filters)}`\n")

    return transformed_path
