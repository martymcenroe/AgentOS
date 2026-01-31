# Test Plan Reviewer

## Problem

Test plans are created manually without automated review. Quality varies significantly:
- Some test plans miss edge cases
- Coverage of acceptance criteria is inconsistent
- Test data requirements are often undocumented
- No structured feedback loop before implementation

## Proposed Solution

Add a Gemini-powered review step for test plans that checks:
- Coverage of acceptance criteria from the source issue
- Edge case identification and boundary testing
- Test data requirements and setup needs
- Security testing considerations
- Performance testing requirements (if applicable)

The reviewer would:
1. Parse the test plan markdown
2. Cross-reference against the original issue's acceptance criteria
3. Generate structured feedback on gaps
4. Provide a PASS/REVISE verdict

## Acceptance Criteria

- [ ] Test plans reviewed before implementation begins
- [ ] Reviewer provides structured feedback with specific line references
- [ ] Integration with existing governance workflow
- [ ] Supports both unit test plans and integration test plans
- [ ] Gemini review prompt follows 0701c pattern (hard-coded, versioned)
- [ ] Audit trail captures test plan versions and review verdicts

## Technical Considerations

- Could extend existing issue workflow with new review step
- Or could be a separate workflow triggered manually
- Prompt should emphasize: "What scenarios are NOT covered?"
- Consider using checklist format for reviewer output

## Related

- Issue #62: Governance Workflow StateGraph
- Issue #101: Governance Workflow Monitoring & E2E Testing
