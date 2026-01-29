# Issue Review: The Janitor: Automated Repository Hygiene Workflow

## Identity Confirmation
I am Gemini 3 Pro, acting as Senior Technical Product Manager & Governance Lead.

## Pre-Flight Gate
PASSED

## Review Summary
The issue is well-defined in terms of user value and scope, but it lacks critical technical details regarding the implied AI components and automation security. Because LangGraph and "human-readable content generation" are specified, cost and data privacy implications must be explicit.

## Tier 1: BLOCKING Issues

### Cost
- [ ] **Model Usage Unspecified:** The technical approach specifies **LangGraph** and the requirements mention "Generates human-readable commit messages." This implies LLM usage. You must explicitly state:
    1. Which model is being used (e.g., Claude 3 Haiku, Sonnet)?
    2. What is the estimated cost per run?
    3. If this is purely deterministic (no LLM), explicitly state "No LLM usage" to clarify why LangGraph is necessary over simple scripts.

### Legal
- [ ] **Data Residency (If LLM used):** If an LLM is used to generate commit messages or analyze code, code snippets will be sent to an external API. You must specify "No External Transmission" (local LLM) or "Compliant Cloud" (e.g., Anthropic via API). This is a privacy blocker.

### Security
- [ ] **Headless Authentication Gap:** The Security section relies on "existing `gh` CLI authentication." However, **Scenario 4** specifies CI/Cron usage. In CI (headless), there is no interactive user. You must specify how auth is handled in automation (e.g., "Supports `GITHUB_TOKEN` environment variable for CI execution").

## Tier 2: HIGH PRIORITY Issues

### Architecture
- [ ] **Test Safety (Live API Calls):** The "Testing Notes" suggest running the actual script against the live GitHub API ("To test issue deduplication..."). This is dangerous for automated testing.
    *   **Requirement:** Add a "Mock Mode" or Interface Adapter requirement so developers can test the workflow logic without actually creating GitHub issues/PRs (or risking a ban for API spam).
    *   **Fix:** Add `n2_reporter` interface abstraction to support a "LocalFileReporter" for testing.

### Quality
- [ ] **Probe Failure Definition:** In "Probe System," it says "Probe failures are isolated." Be specific: does "failure" mean the probe *crashed* (exception) or that it *found issues*? (Assuming the former, but clarify).

## Tier 3: SUGGESTIONS
- **Taxonomy:** Add `maintenance`, `automation`, and `langgraph` labels.
- **Effort:** This looks like a Large (5-8 points) due to the complexity of the State Graph and CLI wrapping.

## Questions for Orchestrator
1. If this uses an LLM for commit messages, do we have a budget cap for "Janitor" runs?

## Verdict
[ ] **APPROVED** - Ready to enter backlog
[x] **REVISE** - Fix Tier 1/2 issues first
[ ] **DISCUSS** - Needs Orchestrator decision