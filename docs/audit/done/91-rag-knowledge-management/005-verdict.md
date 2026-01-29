# Issue Review: The Historian: Automated History Check for Issue Workflow

## Identity Confirmation
I am Gemini 3 Pro, acting as Senior Technical Product Manager & Governance Lead.

## Pre-Flight Gate
PASSED

## Review Summary
The issue is exceptionally well-structured, particularly in its definition of "Fail Open" strategies and "Offline Development" testing. The safety rails are strong. However, there is a specific architectural risk regarding metadata extraction from LLDs that needs clarification before implementation to prevent scope creep.

## Tier 1: BLOCKING Issues
No blocking issues found. Issue is actionable.

### Security
- [ ] No issues found. (Local-only embeddings and read-only access mitigate most risks).

### Safety
- [ ] No issues found. (Fail-open strategy explicitly defined).

### Cost
- [ ] No issues found. (Local compute, no API costs).

### Legal
- [ ] No issues found. (Local data residency confirmed).

## Tier 2: HIGH PRIORITY Issues

### Quality
- [ ] **Subjective Acceptance Criteria:** The criterion "Zero false positives blocking workflow" is subjective and difficult to prove programmatically.
    - **Recommendation:** specific strictly to the threshold logic: "Verify that similarity scores < 0.85 never trigger the 'Duplicate Alert' state."
- [ ] **Empty State Handling:** The requirements do not explicitly define behavior if the `done/` directories are empty or contain fewer than `k=3` documents.
    - **Recommendation:** Add AC: "System handles cases where vector store is empty or has < 3 documents without error."

### Architecture
- [ ] **Metadata Extraction Risk (LLDs):** The requirement "Extract and store issue number... as retrievable metadata" assumes `docs/LLDs/done/*.md` files possess this metadata in a machine-readable format (e.g., YAML frontmatter). If LLDs are free-text, this requires writing a complex parser, which bloats scope.
    - **Recommendation:** Verify if LLD templates currently include `issue_id` in frontmatter. If not, add a prerequisite task to update the LLD template or standard, OR restrict indexing to `audit/` files only for MVP.

## Tier 3: SUGGESTIONS
- **Taxonomy:** Add labels `feature`, `rag`, `workflow-core`.
- **Effort Estimate:** Recommended size: **M** (Medium) - 3 Story Points.
- **Testing:** In "Testing Notes," explicitly state that the "Mocked Vector Store" must be used for CI/CD pipelines to avoid non-deterministic failures based on the actual content of the `done/` folder.

## Questions for Orchestrator
1. Do our current `docs/LLDs/done/*.md` files strictly follow a template with YAML frontmatter containing the Issue ID, or will the developer need to write a regex scraper to find this link?

## Verdict
[ ] **APPROVED** - Ready to enter backlog
[x] **REVISE** - Fix Tier 1/2 issues first
[ ] **DISCUSS** - Needs Orchestrator decision