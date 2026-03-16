# ChantaPermaMemory Local LLM Test Results v0.5.1

## Purpose

This document records the first local LLM feasibility test for ChantaPermaMemory.

The purpose of v0.5.1 was not to fully integrate an LLM into Perma, but to determine:

- whether a local model can be downloaded and executed,
- whether the local runtime environment is stable enough,
- whether the model is suitable for Perma-style assistant tasks,
- and whether the current execution path is practical enough to continue.

## Scope

The following model candidates were tested or prepared for testing:

- `gpt-oss-20b`
- `Nemotron 3 Nano`

At this stage, the actual runtime attempts focused on:

- `gpt-oss-20b` via Hugging Face Transformers
- `gpt-oss-20b` via Ollama
- `NVIDIA-Nemotron-3-Nano-30B-A3B-FP8` via Hugging Face Transformers

## Environment Summary

### Repository / project
- Project: `ChantaPermaMemory`
- Local repository root: `D:\ChantaResearchGroup\ChantaPermaMemory`

### Python environment
- The initial Python 3.14-based environment was discarded for stability concerns.
- A new Python 3.11-based virtual environment was created for Perma.
- `numpy`, `transformers`, `torch`, `accelerate`, `huggingface_hub`, and related dependencies were installed in the Python 3.11 environment.

### Hugging Face
- Hugging Face account authentication was completed successfully.
- A local token was configured.
- `whoami` verification succeeded.

### Ollama
- Ollama was installed locally.
- Direct executable invocation worked.
- `gpt-oss:20b` was pulled and executed successfully through Ollama.

---

## Download Test

### Model 1
- `openai/gpt-oss-20b`

### Model 2
- `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8`

### Result
- Both model snapshots were downloaded successfully to local model directories.
- `gpt-oss:20b` was also pulled successfully through Ollama.

### Notes
- The `gpt-oss-20b` Hugging Face download experienced intermittent network / DNS instability during transfer.
- A resumed download strategy succeeded.
- Download reliability issues were manageable and did not block final acquisition.

---

## Runtime Test Attempt A: gpt-oss-20b via Hugging Face Transformers

### Initial execution path
The first runtime attempt used:

- Hugging Face Transformers
- local model directory
- `pipeline("text-generation", ...)`
- `device_map="auto"`

### Test intention
A simple Perma-style classification prompt was used, such as:

- suggest one candidate domain for a filename,
- explain briefly,
- say uncertain if confidence is weak.

### Execution issues observed

#### Issue A1: missing `accelerate`
The first runtime failure occurred because `device_map="auto"` requires `accelerate`.

##### Resolution
- `accelerate` was installed.

#### Issue A2: disk offload requirement
The next runtime failure indicated that weights were being offloaded to disk and required an explicit `offload_folder`.

##### Resolution
- an offload folder was created and passed into model loading.

#### Issue A3: MXFP4 fallback
The runtime logs indicated that:

- native MXFP4 execution was not available in the current environment,
- the model was being dequantized to `bf16`,
- CPU / disk-offload-based execution was being used.

This matters because it means the test did not run on the intended efficient path.

#### Issue A4: final runtime failure
The final runtime failure was:

- `RuntimeError: expected data_ptr to be aligned to 16 bytes`

This occurred in a MoE execution path involving grouped matrix multiplication while the model was effectively running in a CPU / disk-offload heavy configuration.

### Interim assessment for gpt-oss-20b via Transformers
The `gpt-oss-20b` Hugging Face Transformers runtime path was not practical in the current environment.

---

## Runtime Test Attempt B: Nemotron 3 Nano via Hugging Face Transformers

### Initial execution path
The second runtime attempt used:

- Hugging Face Transformers
- local model directory
- `pipeline("text-generation", ...)`
- `device_map="auto"`
- explicit `offload_folder`

### Test intention
The same Perma-style filename classification prompt was used to compare feasibility across models.

### Execution observations

#### Observation B1: model loading progressed
The Nemotron model did load significantly further and produced a model load report.

The log included a series of `UNEXPECTED` entries, but the report itself also noted that these can be ignorable depending on architecture / task expectations.

#### Observation B2: CPU / disk offload still occurred
The runtime logs showed:

- some parameters were offloaded to CPU and disk,
- the current environment still did not support a clean fully accelerated path.

#### Observation B3: generation warnings were non-fatal
Warnings related to generation flags and deprecations appeared, but these do not appear to be the main reason for failure.

#### Observation B4: final runtime failure
The final runtime failure was again:

- `RuntimeError: expected data_ptr to be aligned to 16 bytes`

This occurred in a MoE grouped matrix multiplication path during inference.

### Interim assessment for Nemotron 3 Nano via Transformers
Although Nemotron is more NVIDIA-oriented in positioning, the practical result in the current environment was materially similar to the `gpt-oss-20b` Transformers attempt:

- model loading could begin,
- but actual inference still failed,
- and the failure again appeared in a grouped MoE execution path under CPU / disk offload conditions.

---

## Runtime Test Attempt C: gpt-oss-20b via Ollama

### Execution path
The third runtime attempt used:

- Ollama local runtime
- `gpt-oss:20b`
- interactive prompt-based testing

### Test prompt
A Perma-style filename classification prompt was used, for example:

- classify a filename into one candidate domain,
- explain briefly,
- say uncertain if confidence is weak.

### Result
The model produced a valid response.

Example behavior observed:
- selected `StatisticalScience` for `SVM-Support-Vector-Machine-D4R6.pdf`
- gave a short explanation that referenced the Support Vector Machine algorithm and its relation to statistical learning

### Assessment
This is the first successful end-to-end local inference result in v0.5.1.

The result suggests that:

- `gpt-oss-20b` itself is not unusable on the current machine,
- the earlier failures were strongly tied to the specific Hugging Face Transformers + offload runtime path,
- Ollama may be a more practical local execution route for Perma than direct Transformers loading in the current setup.

### Limitations
- only a small number of prompts were tested,
- output formatting was still free-form rather than Perma-structured,
- no API integration test was performed yet,
- no systematic latency / throughput measurement was recorded yet.

---

## Cross-Test Interpretation

### Confirmed
The following were confirmed successfully:

- local Hugging Face authentication works,
- the Perma Python 3.11 environment can be created and used,
- both target model snapshots can be downloaded,
- `gpt-oss-20b` can produce a valid local response through Ollama.

### Not confirmed
The following were not achieved successfully:

- stable end-to-end local inference for `gpt-oss-20b` through the current Hugging Face Transformers + offload path,
- stable end-to-end local inference for `Nemotron 3 Nano` through the current Hugging Face Transformers + offload path,
- practical Nemotron inference in the present local setup,
- structured Perma-ready LLM output contract through the current local runtime test.

## Main Diagnosis

### Current best interpretation
The accumulated evidence suggests that the central problem is not simply "large local models do not work."

Instead, the main issue appears to be the current execution route:

- Hugging Face Transformers
- large MoE model
- CPU / disk offload
- current local Windows environment
- grouped matrix multiplication path during inference

That route appears impractical in the current setup.

At the same time, `gpt-oss-20b` running through Ollama shows that the model itself can still be locally usable if the runtime path is more local-friendly.

### Confidence
- Confidence in this diagnosis: **high**
- Reason:
  - two different large MoE model candidates failed in structurally similar ways under the same broad runtime class,
  - `gpt-oss-20b` succeeded once the runtime path changed,
  - this strongly suggests that runtime route is a major determinant of success.

---

## Decision for v0.5.1

### Result
**v0.5.1 is recorded as a partial success overall.**

### Successes
- environment reconfiguration succeeded,
- local authentication succeeded,
- model downloads succeeded,
- `gpt-oss-20b` produced a valid local response through Ollama.

### Failures
- practical inference failed for:
  - `gpt-oss-20b` via current Hugging Face Transformers + offload path
  - `Nemotron 3 Nano` via current Hugging Face Transformers + offload path

### This does *not* mean
It does **not** mean that:

- `gpt-oss-20b` is unusable in all local environments,
- `Nemotron 3 Nano` is unusable in all local environments,
- local LLM use for Perma is a bad direction.

### It *does* mean
It does mean that:

- runtime path matters critically,
- the current Hugging Face Transformers + CPU/disk offload route is not suitable enough in this environment,
- `gpt-oss-20b` remains a viable Perma auxiliary-model candidate through Ollama,
- Nemotron should not currently be treated as a practical local inference candidate under the same tested route.

---

## Recommended Next Directions

The next testing path should consider one or more of the following:

1. continue testing `gpt-oss-20b` through Ollama
   - structured output prompts
   - multiple filename classification cases
   - tag refinement prompts
   - short summary prompts

2. evaluate whether Ollama local API can be used as a Perma auxiliary inference backend

3. defer further time spent on the current failing Hugging Face Transformers + offload path

4. treat Nemotron as a deferred candidate pending a more suitable runtime or hardware/software stack

---

## Relevance to ChantaPermaMemory

This test remains meaningful for Perma because it clarified an important design boundary:

- Perma does not need heavy local model integration immediately,
- and local model adoption should follow a practical runtime path,
- not just a theoretically available model path.

This supports the existing strategy of:

- keeping Perma core logic rule-based through v0.5,
- using LLMs only as auxiliary suggesters,
- and delaying full model integration until runtime feasibility is proven.

At the same time, the Ollama result supports a more optimistic refinement:

- `gpt-oss-20b` can remain in scope as a practical auxiliary local model candidate.

---

## Suggested Status

- Version stage: `v0.5.1`
- Status: `partial success`
- Hugging Face authentication: `success`
- Environment reconfiguration: `success`
- Model downloads: `success`
- `gpt-oss-20b` runtime inference via Transformers/offload: `failed`
- `Nemotron 3 Nano` runtime inference via Transformers/offload: `failed`
- `gpt-oss-20b` runtime inference via Ollama: `success`
- Practical local integration candidate: `gpt-oss-20b via Ollama`
- Deferred candidate: `Nemotron 3 Nano`

## Recommended Next Step

Recommended next step after v0.5.1:

- record the successful Ollama-based `gpt-oss-20b` result,
넌 누구야
edit
Thought for 25.8 seconds
- avoid additional time sink on the current failing Transformers + offload path,
- and move into a small structured-output test set for `gpt-oss-20b` before deciding how to define v0.6.