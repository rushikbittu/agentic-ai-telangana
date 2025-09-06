import os
import pandas as pd
from agents.llm_agent import call_llm_for_cleaning_suggestions


def _iqr_outlier_mask(s: pd.Series) -> pd.Series:
    """Return a boolean Series True where s is an outlier by IQR."""
    s_num = pd.to_numeric(s, errors="coerce").dropna()
    if s_num.empty:
        return pd.Series(False, index=s.index)
    q1, q3 = s_num.quantile(0.25), s_num.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return pd.Series(False, index=s.index)
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return ~s_num.between(lower, upper).reindex(s.index, fill_value=False)


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
    
    # Flag rows with any missing values before cleaning
    df["_qc_missing"] = df.isna().any(axis=1)

    # Generic outlier flags for all numeric columns
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    for col in numeric_cols:
        df[f"_qc_outlier_{col}"] = _iqr_outlier_mask(df[col])

    # Flag rows with missing values before imputation
    imputed_mask = df.isna().any(axis=1)

    # Cleaning: drop duplicates, then impute missing with forward/back fill
    df = df.drop_duplicates()
    df = df.ffill().bfill()

    # Flag rows that had missing values before cleaning
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
        f.write("- `_qc_outlier_<column>`: True if the value in that numeric column was an outlier by IQR rule.\n")
        f.write("- `_qc_imputed`: True if missing values were filled during cleaning.\n")

    return cleaned_path
