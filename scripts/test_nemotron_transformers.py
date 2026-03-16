from pathlib import Path

import torch
from transformers import pipeline

MODEL_DIR = Path(r"D:\Models\nemotron-3-nano-fp8")
OFFLOAD_DIR = Path(r"D:\ChantaResearchGroup\ChantaPermaMemory\offload\nemotron-3-nano")

print("[INFO] Checking environment...")
print(f"[INFO] Model dir     : {MODEL_DIR}")
print(f"[INFO] Offload dir   : {OFFLOAD_DIR}")
print(f"[INFO] CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"[INFO] CUDA device   : {torch.cuda.get_device_name(0)}")
    total_vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    print(f"[INFO] VRAM (GB)     : {total_vram_gb:.2f}")

print("[INFO] Loading pipeline...")

pipe = pipeline(
    "text-generation",
    model=str(MODEL_DIR),
    dtype="auto",
    device_map="auto",
    model_kwargs={
        "offload_folder": str(OFFLOAD_DIR),
    },
)

prompt = (
    "Classify this filename into one candidate domain for Chanta Research Group and explain briefly.\n\n"
    "Filename: SVM-Support-Vector-Machine-D4R6.pdf\n\n"
    "Possible domains:\n"
    "- ProcessIntelligenceLab\n"
    "- StatisticalScience\n"
    "- PythonProgramming\n"
    "- ChantaPrivateBanking/Macro\n\n"
    "If uncertain, say uncertain."
)

print("[INFO] Running inference...")

outputs = pipe(
    prompt,
    max_new_tokens=32,
    do_sample=False,
)

print("[OK] Inference finished.")
print("=" * 80)
print(outputs[0]["generated_text"])
print("=" * 80)