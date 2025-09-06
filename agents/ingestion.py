import os
import pandas as pd
import httpx

def load_dataset(source_config, output_dir):
    dtype = source_config.get("type", "file")
    location = source_config["location"]

    if dtype == "file":
        df = pd.read_csv(location)
    elif dtype == "url":
        r = httpx.get(location)
        r.raise_for_status()
        import io
        df = pd.read_csv(io.BytesIO(r.content))
    else:
        raise ValueError(f"Unknown dataset source type: {dtype}")

    raw_path = os.path.join(output_dir, "raw.csv")
    df.to_csv(raw_path, index=False)
    # New: ingestion summary 
    dataset_name = os.path.basename(location)
    summary_path = os.path.join(output_dir, "01_ingestion_summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"# Ingestion Summary\n\n")
        f.write(f"- **Dataset name:** `{dataset_name}`\n")
        f.write(f"- **Rows x Cols:** {df.shape[0]} x {df.shape[1]}\n")
        f.write(f"- **Columns:** {', '.join(map(str, df.columns))}\n\n")
        try:
            f.write("## Preview (first 5 rows)\n\n")
            f.write(df.head(5).to_markdown(index=False))
            f.write("\n")
        except Exception:
            pass

    return raw_path
