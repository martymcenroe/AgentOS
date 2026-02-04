# LLD Review: #91 - The Historian - Automated History Check

## Identity Confirmation
I am Gemini 3 Pro, acting as Senior Software Architect & AI Governance Lead.

## Pre-Flight Gate
**PASSED**

## Review Summary
The design for the "Historian" node is robust, featuring a well-defined "Fail Open" strategy and clear threshold logic. The architectural integration with the existing Librarian infrastructure is efficient. However, the Test Plan (Section 10) completely overlooks the `tools/rebuild_knowledge_base.py` modifications. Requirements 1 and 2 (indexing behavior) are undefined in the test strategy, resulting in low requirement coverage. This prevents approval.

## Open Questions Resolved
- [x] ~~Should we support custom thresholds via configuration in a future iteration?~~ **RESOLVED: Yes, defer to backlog. Maintain hardcoded constants for MVP per ADR.**
- [x] ~~No open questions found in Section 1.~~ (N/A - Question above answered)

## Requirement Coverage Analysis (MANDATORY)

**Section 3 Requirements:**
| # | Requirement | Test(s) | Status |
|---|-------------|---------|--------|
| 1 | Vector store indexes `docs/audit/done` with metadata | - | **GAP** |
| 2 | Vector store indexes `docs/LLDs/done` with metadata | - | **GAP** |
| 3 | Historian node embeds using local SentenceTransformers | T010-T040 (Implicit via node exec) | ✓ Covered |
| 4 | Similarity >= 0.85 triggers Duplicate Alert | T040, T090, T100 | ✓ Covered |
| 5 | Similarity 0.5 - 0.85 appends context | T030, T060, T070, T080 | ✓ Covered |
| 6 | Similarity < 0.5 proceeds unchanged | T010, T020, T050 | ✓ Covered |
| 7 | Technical failures log warning and proceed (Fail Open) | T110, T120, T130 | ✓ Covered |
| 8 | Empty/Sparse store handled gracefully | T140, T150 | ✓ Covered |
| 9 | User decisions are logged | T200, T210, T220 (Flow only, logging not verified) | **GAP** |
| 10 | Threshold boundary exactness (0.85) | T090 | ✓ Covered |

**Coverage Calculation:** 7 requirements covered / 10 total = **70%**

**Verdict: BLOCK** (Must be ≥95%)

**Missing Test Scenarios:**
1.  **Test for Req 1 & 2:** Unit tests for `tools/rebuild_knowledge_base.py::index_history_documents`. Needs to verify it correctly scans directories, extracts metadata (YAML vs Filename), and calls the embedding function.
2.  **Test for Req 9:** Update T200-T220 to explicitly assert that a log message was emitted (using `caplog` fixture).

## Tier 1: BLOCKING Issues
No blocking issues found in Tier 1 categories. LLD is approved for implementation pending Tier 2 fixes.

### Cost
- [ ] No issues found. Local execution ensures zero API costs.

### Safety
- [ ] No issues found. Fail Open strategy prevents workflow blocking.

### Security
- [ ] No issues found. Local embeddings protect brief content.

### Legal
- [ ] No issues found.

## Tier 2: HIGH PRIORITY Issues

### Architecture
- [ ] No issues found.

### Observability
- [ ] No issues found.

### Quality
- [ ] **Requirement Coverage:** **BLOCK**. Coverage is 70%. You must add unit tests for `tools/rebuild_knowledge_base.py`. The current test plan only covers `agentos/nodes/historian.py`. The ingestion logic (extracting IDs, handling file paths) is complex and requires TDD.
- [ ] **Logging Assertions:** Tests T200, T210, and T220 should explicitly verify that user actions are logged (Req 9), not just that the workflow proceeds.

## Tier 3: SUGGESTIONS
- **Metadata Extraction:** Consider adding a test case for a file with *malformed* YAML frontmatter to ensure it falls back to the filename strategy gracefully (robustness).
- **Performance:** For `rebuild_knowledge_base.py`, considering printing a progress bar if the document count is high, as embedding generation can be slow.

## Questions for Orchestrator
1. None.

## Verdict
[ ] **APPROVED** - Ready for implementation
[x] **REVISE** - Fix Tier 1/2 issues first
[ ] **DISCUSS** - Needs Orchestrator decision