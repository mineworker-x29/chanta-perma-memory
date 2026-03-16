from pathlib import Path
from huggingface_hub import snapshot_download

TARGET_DIR = Path(r"D:\Models\nemotron-3-nano-fp8")

print("[INFO] Starting download...")
print(f"[INFO] Target directory: {TARGET_DIR}")

downloaded_path = snapshot_download(
    repo_id="nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8",
    local_dir=str(TARGET_DIR),
)

print("[OK] Download finished.")
print(f"[OK] Downloaded to: {downloaded_path}")