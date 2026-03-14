# AGENTS.md

This repository contains the code and design documents for ChantaPermaMemory.

## Mission

Build a local-first memory and repository management system for Chanta Research Group.

## Important Constraints

1. Do not assume that the user's real source materials live inside this repo.
2. Do not implement irreversible file deletion or aggressive auto-moving behavior in early stages.
3. Prefer dry-run behavior for ingest, classification, and organization features.
4. Prefer small, reviewable changes over large sweeping refactors.
5. Keep fact / interpretation / hypothesis distinctions in mind when designing data structures.
6. Prefer explicit config and transparent behavior over hidden automation.

## Early Priorities

1. project scaffolding
2. config loading
3. metadata schemas
4. inbox scanning
5. dry-run ingest pipeline
6. archive-safe behaviors
7. tests for deterministic policy logic
