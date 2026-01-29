# Improve Issue Template Based on Gemini Verdict Analysis

## User Story
As a workflow user,
I want Claude to pass Gemini's Pre-Flight Gate on the first or second try,
So that issue creation completes faster with less back-and-forth.

## Objective
Analyze historical Gemini verdicts to identify common feedback patterns, then revise the issue template (0101) to preemptively address those patterns and improve first-pass approval rates.

## UX Flow

### Scenario 1: Running the Verdict Audit
1. User runs `python tools/audit_verdicts.py`
2. Script scans all verdict files in `docs/audit/active/*/` and `docs/audit/done/*/`
3. Script extracts and categorizes all feedback by tier and theme
4. Script generates `docs/reports/verdict-audit-report.md` with findings
5. Result: User sees top 10 most common issues and recommended template changes

### Scenario 2: No Verdict Files Found
1. User runs `python tools/audit_verdicts.py`
2. Script finds no verdict files in expected directories
3. Script outputs: "No verdict files found. Checked: docs/audit/active/, docs/audit/done/"
4. Result: Script exits gracefully with non-zero status

### Scenario 3: Validating Template Improvements
1. User creates test issues using revised template
2. User submits to Gemini Pre-Flight Gate
3. User compares first-pass rate to baseline
4. Result: Measurable improvement in approval rate

## Requirements

### Audit Phase
1. Scan all `*-verdict.md` files in `docs/audit/active/*/` and `docs/audit/done/*/`
2. Parse verdict structure to extract:
   - Overall verdict (APPROVED/REVISE/REJECT)
   - Tier 1 (BLOCKING) issues with descriptions
   - Tier 2 (HIGH PRIORITY) issues with descriptions
   - Tier 3 (SUGGESTIONS) with descriptions
3. Categorize each feedback item by theme:
   - Missing sections (e.g., Security, UX Flow, Dependencies)
   - Vague requirements (non-testable criteria)
   - Scope issues (too broad, missing Out of Scope)
   - Technical gaps (missing approach details)
   - Documentation gaps (missing file inventory, reports)
4. Count occurrences per category and rank by frequency
5. Generate structured report with top 10 patterns

### Template Revision Phase
1. Add inline guidance for frequently-failed sections
2. Add concrete examples for ambiguous placeholders
3. Add validation prompts (e.g., "Is this criterion testable?")
4. Expand "Tips for Good Issues" with patterns from Gemini feedback
5. Add common mistake warnings where applicable

### Validation Phase
1. Select 5 representative briefs of varying complexity
2. Generate issues using both old and new templates
3. Submit to Gemini Pre-Flight Gate
4. Record first-pass rate (APPROVED without revision)
5. Document comparison in implementation report

## Technical Approach
- **Audit script (`audit_verdicts.py`):** Uses pathlib to scan directories, regex to extract verdict sections, Counter for frequency analysis
- **Pattern classification:** Keyword matching against predefined category dictionary (extensible)
- **Report generation:** Markdown output with tables, sorted by frequency
- **Template updates:** Manual edits informed by audit findings

## Security Considerations
- Script only reads local markdown files — no external access
- No user data or credentials involved
- No file modifications except report generation to known path

## Files to Create/Modify
- `tools/audit_verdicts.py` — New script to analyze verdict files and generate report
- `docs/reports/verdict-audit-report.md` — Generated report with findings and recommendations
- `docs/templates/0101-issue-template.md` — Revised template with improvements based on findings

## Dependencies
- None — this is a standalone improvement

## Out of Scope (Future)
- Modifying the Gemini review prompt (0701c) — focus on template only
- Automating template validation — manual review for now
- Reprocessing existing issues — improvements apply to future issues only
- Creating a feedback loop to continuously update template — single audit pass

## Acceptance Criteria
- [ ] `audit_verdicts.py` successfully scans both `docs/audit/active/*/` and `docs/audit/done/*/`
- [ ] Script handles missing directories gracefully without crashing
- [ ] Audit report includes frequency-ranked list of top 10 feedback patterns
- [ ] Each pattern includes: category, count, example feedback, recommended fix
- [ ] Template includes new inline guidance for at least 5 sections
- [ ] "Tips for Good Issues" expanded with at least 3 new tips from audit findings
- [ ] Validation testing shows ≥20% improvement in first-pass rate
- [ ] All new files added to `docs/0003-file-inventory.md`

## Definition of Done

### Implementation
- [ ] `audit_verdicts.py` implemented with CLI interface
- [ ] Report generation produces valid markdown
- [ ] Template revised with audit-informed improvements

### Tools
- [ ] `tools/audit_verdicts.py` documented with usage in header
- [ ] Script supports `--help` flag for usage info

### Documentation
- [ ] Audit report explains methodology and findings
- [ ] Template changes documented in report
- [ ] Validation results included in implementation report
- [ ] Add new files to `docs/0003-file-inventory.md`

### Reports (Pre-Merge Gate)
- [ ] `docs/reports/{IssueID}/implementation-report.md` created
- [ ] `docs/reports/{IssueID}/test-report.md` created

### Verification
- [ ] Run 0817 Wiki Alignment Audit - PASS (if wiki updated)

## Testing Notes
- **Baseline measurement:** Before template changes, run 5 briefs through current template and record first-pass rate
- **Post-revision measurement:** Same 5 briefs with revised template, compare results
- **Edge cases to test:**
  - Brief with minimal information (should get more guidance from template)
  - Brief with complex multi-component feature (should get better structure)
  - Brief with security implications (should prompt for Security Considerations)
- **Success metric:** Average iterations per issue should decrease; target ≥20% improvement in first-pass rate