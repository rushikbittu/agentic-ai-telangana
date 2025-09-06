import os
from datetime import datetime

def log_event(message, output_dir):
    logfile = os.path.join(output_dir, "run.log")
    with open(logfile, "a") as f:
        timestamp = datetime.now().isoformat()
        f.write(f"[{timestamp}] {message}\n")
