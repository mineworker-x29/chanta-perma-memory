# Changelog

All notable changes to ChantaPermaMemory will be documented in this file.

## v1.0
- Added `generate_review_report.py` for human-readable inbox review
- Added `build_perma_v1_snapshot.py` for final v1 system snapshot
- Added `run_perma_v1.py` as integrated end-to-end pipeline runner
- Unified scanning, review, memory candidate generation, LLM-assisted refinement, and final snapshot packaging
- Established ChantaPermaMemory as a local-first, reviewable, conservative memory/repository assistant

## v0.9
- Added local LLM-assisted refinement of provisional memory candidates
- Added `scripts/refine_memory_candidates_with_ollama.py`
- Introduced Ollama-backed structured refinement for candidate content, reason, and confidence
- Kept memory refinement conservative by restricting LLM output to existing candidate evidence

## v0.8
- Added initial memory layer candidate generation
- Added `schemas/memory_candidate.schema.json`
- Added `scripts/generate_memory_candidates.py`
- Introduced provisional memory candidates derived from manifest items
- Separated repository item observations from memory-layer candidate objects

## v0.7
- Added light content parsing for `.txt` and `.md` files
- Added `content_preview` and `content_preview_source` fields to inbox manifest items
- Extended domain suggestion to optionally use file content preview
- Extended tag suggestion to optionally use file content preview
- Shifted Perma from filename-only suggestion toward light content-aware classification

## v0.6
- Added markdown review report generation from inbox manifest
- Added `scripts/generate_review_report.py`
- Added summary sections for candidate domains, extensions, confidence, tags, ambiguous items, and full item review
- Extended Perma from scanning and suggestion into human-review support

## v0.5
- Added rule-based tag suggestion
- Added `policies/tag_rules.json`
- Updated inbox scanner to populate retrieval-oriented tags
- Added extension, keyword, and domain-derived tag suggestions

## v0.4
- Added rule-based candidate domain suggestion
- Added `policies/domain_rules.json`
- Updated inbox scanner to populate `candidate_domain`
- Added confidence output for simple rule-based domain suggestions

## v0.3
- Added `config/config.json`
- Separated repository paths and scan behavior from code
- Updated `scan_inbox.py` to load settings from config
- Improved portability by removing hardcoded operational paths

## v0.2
- Added manifest version field to inbox scan output
- Added `schemas/inbox_manifest.schema.json`
- Formalized inbox manifest output structure

## v0.1
- Established initial repository documentation
- Added repository specification document
- Added persona and memory governance document
- Implemented initial dry-run inbox scanner
- Added basic inbox manifest generation