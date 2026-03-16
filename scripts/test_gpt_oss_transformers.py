from transformers import pipeline

MODEL_DIR = r"D:\Models\gpt-oss-20b"
OFFLOAD_DIR = r"D:\ChantaResearchGroup\ChantaPermaMemory\offload\gpt-oss-20b"

print("[INFO] Loading pipeline...")

pipe = pipeline(
    "text-generation",
    model=MODEL_DIR,
    dtype="auto",
    device_map="auto",
    model_kwargs={
        "offload_folder": OFFLOAD_DIR,
    },
)

messages = [
    {
        "role": "user",
        "content": (
            "Classify this filename into one candidate domain for Chanta Research Group "
            "and explain briefly:\n"
            "SVM-Support-Vector-Machine-D4R6.pdf\n\n"
            "Possible domains:\n"
            "- ProcessIntelligenceLab\n"
            "- StatisticalScience\n"
            "- PythonProgramming\n"
            "- ChantaPrivateBanking/Macro\n\n"
            "If uncertain, say uncertain."
        )
    }
]

print("[INFO] Running inference...")

outputs = pipe(
    messages,
    max_new_tokens=256,
)

print("[OK] Inference finished.")
print(outputs[0]["generated_text"][-1])