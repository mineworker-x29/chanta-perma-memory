{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://chanta.local/schemas/perma_v1_snapshot.schema.json",
  "title": "PermaV1Snapshot",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "perma_version",
    "generated_at",
    "components",
    "summary"
  ],
  "properties": {
    "perma_version": {
      "type": "string",
      "const": "1.0"
    },
    "generated_at": {
      "type": "string",
      "format": "date-time"
    },
    "components": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "manifest_path",
        "review_report_path",
        "memory_candidates_path",
        "memory_candidates_refined_path"
      ],
      "properties": {
        "manifest_path": { "type": "string" },
        "review_report_path": { "type": "string" },
        "memory_candidates_path": { "type": "string" },
        "memory_candidates_refined_path": { "type": ["string", "null"] }
      }
    },
    "summary": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "item_count",
        "memory_candidate_count",
        "refined_candidate_count"
      ],
      "properties": {
        "item_count": { "type": "integer", "minimum": 0 },
        "memory_candidate_count": { "type": "integer", "minimum": 0 },
        "refined_candidate_count": { "type": "integer", "minimum": 0 }
      }
    }
  }
}