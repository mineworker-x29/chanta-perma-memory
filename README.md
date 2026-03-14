# ChantaPermaMemory

Local-first memory, repository organization, and retrieval preparation system for Chanta Research Group.

## Overview

ChantaPermaMemory is the memory and repository management layer of Chanta Research Group. Its purpose is not merely to generate text, but to organize, preserve, classify, prepare, and retrieve knowledge assets across the user's local research repository.

## Core Role

ChantaPermaMemory is responsible for:
- organizing the local repository
- classifying and tagging materials
- preparing materials for retrieval
- deciding what should become durable memory
- separating fact, interpretation, and hypothesis where possible
- helping surface cross-document insight from the repository

## Design Principles

1. Local-first
2. System over model
3. Conservative memory write
4. Separation of layers
5. Fact-first organization

## Suggested Initial Layout

```text
ChantaPermaMemory/
  README.md
  docs/
  schemas/
  prompts/
  policies/
  scripts/
  tests/
```

## Python Scaffold (v0.1)

```text
src/chanta_perma_memory/
  cli.py
  config/
  schemas/
  policies/
```

- CLI entrypoint: `chanta-perma-memory`
- Current ingest behavior is dry-run only
- No file move or delete execution is implemented in this stage
