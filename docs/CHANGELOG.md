# Changelog

All notable changes to ChantaPermaMemory will be documented in this file.

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