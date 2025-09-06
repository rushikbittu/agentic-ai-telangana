import os
import pandas as pd
from agents.llm_agent import call_llm_for_cleaning_suggestions

def clean_data(std_path, config, output_dir):
    df = pd.read_csv(std_path)
    n_rows_before = len(df)
    dup_count = df.duplicated().sum()
    missing_before = df.isna().sum()
    total_missing_before = int(missing_before.sum())
    try:
        _ = call_llm_for_cleaning_suggestions(df.head(100).to_dict(), config)
    except Exception:
        _ = None  
    df["_qc_missing"] = df.isna().any(axis=1)
    if "rain_(mm)" in df.columns:
        s = pd.to_numeric(df["rain_(mm)"], errors="coerce")
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        df["_qc_outlier_rain"] = ~s.between(lower, upper)
    imputed_mask = df.isna().any(axis=1)

    # cleaning 
    df = df.drop_duplicates()
    df = df.ffill().bfill() 

    df["_qc_imputed"] = imputed_mask
    
    n_rows_after = len(df)
    missing_after = df.isna().sum()
    total_missing_after = int(missing_after.sum())

    # Save cleaned data
    cleaned_path = os.path.join(output_dir, "cleaned.csv")
    df.to_csv(cleaned_path, index=False)

    # --- Cleaning summary ---
    summary_path = os.path.join(output_dir, "03_cleaning_summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("# Cleaning Summary\n\n")
        f.write(f"- **Rows before:** {n_rows_before}\n")
        f.write(f"- **Duplicates removed:** {dup_count}\n")
        f.write(f"- **Rows after:** {n_rows_after}\n")
        f.write(f"- **Missing values (total) before:** {total_missing_before}\n")
        f.write(f"- **Missing values (total) after:** {total_missing_after}\n\n")

        f.write("## Missing values by column (before)\n\n")
        f.write(missing_before.to_frame("missing_count").to_markdown())
        f.write("\n\n## Missing values by column (after)\n\n")
        f.write(missing_after.to_frame("missing_count").to_markdown())
        f.write("\n\n")

        f.write("## Notes on Quality Flags\n\n")
        f.write("- `_qc_missing`: True if the row had any missing values before cleaning.\n")
        f.write("- `_qc_outlier_rain`: True if rainfall was detected as an outlier (IQR rule).\n")
        f.write("- `_qc_imputed`: True if missing values were filled during cleaning.\n")

    return cleaned_path
