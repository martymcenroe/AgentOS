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
2. Script scans all verdict files in `docs/audit/active/*/` and `docs/audit/done/*/` (default paths)
3. Script extracts and categorizes all feedback by tier and theme
4. Script generates `docs/reports/verdict-audit-report.md` with findings
5. Result: User sees top 10 most common issues and recommended template changes

### Scenario 2: Running with Custom Paths
1. User runs `python tools/audit_verdicts.py --scan-dir /path/to/custom/audit`
2. Script scans all verdict files in the specified directory
3. Script generates report to default location (or `--output` if specified)
4. Result: User can audit verdict files from any location

### Scenario 3: No Verdict Files Found
1. User runs `python tools/audit_verdicts.py`
2. Script finds no verdict files in expected directories
3. Script outputs: "No verdict files found. Checked: docs/audit/active/, docs/audit/done/"
4. Result: Script exits gracefully with non-zero status

### Scenario 4: JSON Output for Programmatic Use
1. User runs `python tools/audit_verdicts.py --json`
2. Script performs analysis and outputs JSON to stdout
3. Result: Output can be piped to other tools or processed programmatically

### Scenario 5: Validating Template Improvements
1. User creates 3 test issues using revised template (manual process)
2. User submits to Gemini Pre-Flight Gate
3. User compares first-pass rate to baseline
4. Result: Measurable improvement in approval rate

## Requirements

### Audit Phase
1. Accept CLI arguments for paths via `--scan-dir` with defaults to `docs/audit/active/` and `docs/audit/done/`
2. Scan all `*-verdict.md` files in specified directories
3. Parse verdict structure to extract:
   - Overall verdict (APPROVED/REVISE/REJECT)
   - Tier 1 (BLOCKING) issues with descriptions
   - Tier 2 (HIGH PRIORITY) issues with descriptions
   - Tier 3 (SUGGESTIONS) with descriptions
4. Categorize each feedback item by theme:
   - Missing sections (e.g., Security, UX Flow, Dependencies)
   - Vague requirements (non-testable criteria)
   - Scope issues (too broad, missing Out of Scope)
   - Technical gaps (missing approach details)
   - Documentation gaps (missing file inventory, reports)
5. Count occurrences per category and rank by frequency
6. Generate structured report with top 10 patterns

### Template Revision Phase
1. Add inline guidance for frequently-failed sections
2. Add concrete examples for ambiguous placeholders
3. Add validation prompts (e.g., "Is this criterion testable?")
4. Expand "Tips for Good Issues" with patterns from Gemini feedback
5. Add common mistake warnings where applicable

### Validation Phase
1. Select 3 representative briefs of varying complexity (manual selection)
2. Generate issues using both old and new templates (manual process — no LLM API usage)
3. Submit to Gemini Pre-Flight Gate
4. Record first-pass rate (APPROVED without revision)
5. Document comparison in implementation report

## Technical Approach
- **Audit script (`audit_verdicts.py`):** Uses Python standard library only (pathlib, re, collections, argparse, json). No external dependencies required.
- **CLI interface:** Accepts `--scan-dir` (repeatable), `--output`, `--json`, `--help` flags
- **Pattern classification:** Keyword matching against predefined category dictionary (extensible)
- **Report generation:** Markdown output with tables, sorted by frequency (or JSON with `--json` flag)
- **Template updates:** Manual edits informed by audit findings

## Security Considerations
- Script only reads local markdown files — no external access
- No user data or credentials involved
- No file modifications except report generation to known path
- CLI arguments validated to prevent path traversal

## Files to Create/Modify
- `tools/audit_verdicts.py` — New script to analyze verdict files and generate report
- `docs/reports/verdict-audit-report.md` — Generated report with findings and recommendations
- `docs/templates/0101-issue-template.md` — Revised template with improvements based on findings

## Dependencies
- None — uses Python standard library only (pathlib, re, collections, argparse, json)

## Out of Scope (Future)
- Modifying the Gemini review prompt (0701c) — focus on template only
- Automating template validation — manual review for now
- Reprocessing existing issues — improvements apply to future issues only
- Creating a feedback loop to continuously update template — single audit pass
- LLM-assisted validation — validation is manual to avoid API costs

## Acceptance Criteria
- [ ] `audit_verdicts.py` successfully scans both `docs/audit/active/*/` and `docs/audit/done/*/`
- [ ] Script accepts `--scan-dir` argument to override default paths
- [ ] Script supports `--json` flag for JSON output
- [ ] Script handles missing directories gracefully without crashing
- [ ] Audit report includes frequency-ranked list of top 10 feedback patterns
- [ ] Each pattern includes: category, count, example feedback, recommended fix
- [ ] Template includes new inline guidance for at least 5 sections
- [ ] "Tips for Good Issues" expanded with at least 3 new tips from audit findings
- [ ] Validation testing shows ≥20% improvement in first-pass rate (based on 3 manual test issues)
- [ ] All new files added to `docs/0003-file-inventory.md`
- [ ] Unit tests created for `audit_verdicts.py` covering path parsing and regex logic

## Definition of Done

### Implementation
- [ ] `audit_verdicts.py` implemented with CLI interface
- [ ] Report generation produces valid markdown
- [ ] Template revised with audit-informed improvements
- [ ] Unit tests written and passing

### Tools
- [ ] `tools/audit_verdicts.py` documented with usage in header
- [ ] Script supports `--help` flag for usage info
- [ ] Script supports `--scan-dir` for custom paths
- [ ] Script supports `--json` for programmatic output

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
- [ ] Unit tests passed for `audit_verdicts.py`

## Testing Notes
- **Baseline measurement:** Before template changes, run 3 briefs through current template and record first-pass rate (manual process)
- **Post-revision measurement:** Same 3 briefs with revised template, compare results (manual process)
- **Unit test coverage:**
  - Path parsing with valid/invalid inputs
  - Regex extraction of verdict sections
  - Category classification logic
  - Edge case: empty verdict file
  - Edge case: malformed verdict structure
- **Edge cases to test:**
  - Brief with minimal information (should get more guidance from template)
  - Brief with complex multi-component feature (should get better structure)
  - Brief with security implications (should prompt for Security Considerations)
- **Success metric:** Average iterations per issue should decrease; target ≥20% improvement in first-pass rate

## Labels
`enhancement`, `template`, `governance`, `workflow`, `tooling`, `process`

## Original Brief
# Improve Issue Template Based on Gemini Verdict Analysis

Audit all Gemini verdicts to identify patterns in feedback, then revise the issue template so Claude passes review with fewer iterations.

## User Story
As a workflow user,
I want Claude to pass Gemini's Pre-Flight Gate on the first or second try,
So that issue creation completes faster with less back-and-forth.

## Objective
Analyze historical Gemini verdicts to identify common feedback patterns, then revise the issue template (0101) to preemptively address those patterns.

## Requirements

### Audit Phase
1. Collect all verdict files from `docs/audit/active/*/` and `docs/audit/done/*/`
2. Extract feedback from each verdict:
   - Pre-Flight Gate failures
   - Tier 1 (BLOCKING) issues
   - Tier 2 (HIGH PRIORITY) issues
   - Tier 3 (SUGGESTIONS)
3. Categorize feedback by theme (e.g., missing sections, vague requirements, security gaps)
4. Identify the top 5-10 most common issues

### Template Revision Phase
1. Update template sections to address common feedback
2. Add guidance/examples for sections that frequently fail
3. Add prompts/placeholders that prevent common omissions
4. Update the "Tips for Good Issues" section with patterns from Gemini feedback

### Validation Phase
1. Test revised template with 3-5 representative briefs
2. Measure first-pass rate (verdicts that come back APPROVED without revisions)
3. Compare to baseline (current first-pass rate)

## Technical Approach
- **Audit script:** Python script to scan verdict files and extract structured feedback
- **Pattern analysis:** Group feedback by category, count occurrences
- **Report generation:** Create audit report with findings and recommendations
- **Template updates:** Manual edits to `docs/templates/0101-issue-template.md`

## Files to Create/Modify
- `tools/audit_verdicts.py` — Script to analyze verdict files
- `docs/reports/verdict-audit-report.md` — Findings and recommendations
- `docs/templates/0101-issue-template.md` — Revised template with improvements

## Acceptance Criteria
- [ ] Audit script processes all verdict files in audit directories
- [ ] Audit report identifies top 5-10 common feedback patterns
- [ ] Template revised to address identified patterns
- [ ] First-pass rate improves by at least 20% in validation testing
- [ ] Documentation updated with new template guidance

## Out of Scope
- Changing the review prompt (0701c) — focus on improving template only
- Modifying workflow logic — pure template improvement
- Reprocessing old issues — this is for future issues only

## Testing Notes
- Baseline measurement: Run 5 test briefs with current template, measure first-pass rate
- Post-revision measurement: Run same 5 briefs with revised template, compare results
- Success metric: Reduction in average iterations per issue