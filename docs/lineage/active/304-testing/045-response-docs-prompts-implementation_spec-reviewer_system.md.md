The file `docs/prompts/implementation_spec/reviewer_system.md` has been written. It contains the Gemini system prompt for implementation readiness review, including:

- **Metadata** matching the drafter_system.md pattern (version, model, issue reference)
- **Identity** section defining the reviewer's role as quality gate between spec and implementation
- **Scope** clarifying what IS and IS NOT being reviewed (executability, not code quality)
- **6 review criteria** with checkpoint tables (File Coverage, Specificity, Concreteness, Pattern Consistency, Feasibility, Test Guidance) — each with severity levels (BLOCKING / HIGH PRIORITY / SUGGESTION)
- **Verdict definitions** for APPROVED, REVISE, and BLOCKED with specific guidance on when to use each
- **Revision review** instructions for iteration > 0 (focus on prior feedback, watch for regressions)
- **Required output format** with the structured markdown template matching the `parse_review_verdict()` parser expectations (`[X]` checkboxes)
- **Constraints** preventing scope creep and ensuring actionable feedback

What do you want to work on next?
