from pathlib import Path
from huggingface_hub import snapshot_download

TARGET_DIR = Path(r"D:\Models\gpt-oss-20b")

print("[INFO] Starting download...")
print(f"[INFO] Target directory: {TARGET_DIR}")

downloaded_path = snapshot_download(
    repo_id="openai/gpt-oss-20b",
    local_dir=str(TARGET_DIR),
)

print("[OK] Download finished.")
print(f"[OK] Downloaded to: {downloaded_path}")