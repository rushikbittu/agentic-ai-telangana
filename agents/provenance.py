import os
import json
import hashlib
import platform
import subprocess
from datetime import datetime

def file_checksum(path):
    """Compute SHA-256 checksum for a file (used for provenance)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def save_run_metadata(output_dir, config_path, dataset_path=None, llm_model=None):
    """Save provenance metadata for reproducibility and audit."""
    meta = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user": os.getenv("USERNAME") or os.getenv("USER"),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "git_commit": None,
        "config_path": config_path,
        "dataset_checksum": file_checksum(dataset_path) if dataset_path and os.path.exists(dataset_path) else None,
        "llm_model": llm_model,
        "requirements": None,
    }

    if os.path.exists(".git"):
        try:
            commit = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True, text=True
            )
            meta["git_commit"] = commit.stdout.strip()
        except Exception:
            pass

    # Try to capture pip freeze
    try:
        reqs = subprocess.run(
            ["pip", "freeze"], capture_output=True, text=True
        )
        meta["requirements"] = reqs.stdout.splitlines()
    except Exception:
        pass

    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "run_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    return meta
