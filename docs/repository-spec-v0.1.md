# ChantaPermaMemory Repository Spec v0.1

## Purpose

This document defines the initial operating structure for the local Chanta Research Group repository that ChantaPermaMemory will observe, organize, and support.

## Main Assumption

The local serious-material repository is centered around:

```text
D:/ChantaResearchGroup/
```

## Initial Top-Level Structure

```text
D:/ChantaResearchGroup/
  00_Inbox/
  01_ProcessIntelligenceLab/
  02_StatisticalScience/
  03_PythonProgramming/
  04_ChantaPrivateBanking/
  90_Shared/
  99_Archive/
  ChantaPermaMemory/
```

## Folder Roles

### 00_Inbox
- initial landing zone for new materials
- temporary holding area before classification

### Domain folders
- primary long-term home for domain-centered materials

### 90_Shared
- cross-domain materials
- resources with no single clean home

### 99_Archive
- inactive or low-priority materials kept for record and future retrieval

### ChantaPermaMemory
- code and system repository for Perma itself

## Initial Placement Rules

- new items may enter `00_Inbox` first
- clear single-domain items may go directly to their domain folder
- ambiguous items may remain in `90_Shared`
- inactive but useful items should move to `99_Archive`

## Metadata Over Folder Purity

Perma should eventually rely more on metadata than on increasingly complex folder trees.

Example metadata fields:
- domain
- topic
- type
- status
- source
- confidence
- related_project
- related_entities
- tags
