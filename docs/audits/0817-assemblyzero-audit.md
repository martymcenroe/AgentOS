# 0817 - AssemblyZero Health Check

## Purpose

Verify the documentation system (Agent Operating System) itself is healthy and internally consistent. Unlike other audits that check code/product, this audit checks the operating system that agents run on.

## Trigger

- Monthly (system maintenance)
- When onboarding new agents
- After major documentation reorganization
- When agents report confusion or broken workflows

## Philosophy

> "The operating system must be debuggable."

If an agent can't execute a protocol because of broken references, unclear instructions, or conflicting guidance, the AOS has a bug.

## Procedure

### Step 1: Cross-Reference Validation

**Check for broken internal references:**
```bash
# Find all doc references and verify targets exist
grep -roh "docs/[0-9]\{4\}[^.]*\.md" docs/*.md | sort -u | while read ref; do
  if [ ! -f "$ref" ]; then
    echo "BROKEN: $ref"
  fi
done

# Find references to deleted docs (common after renumbering)
grep -r "0011" docs/*.md --include="*.md" | grep -v session-logs
```

**Check for orphaned docs (not referenced anywhere):**
```bash
for f in docs/0*.md; do
  basename="$(basename $f)"
  refs=$(grep -r "$basename" docs/*.md --include="*.md" -l | wc -l)
  if [ "$refs" -eq 0 ]; then
    echo "ORPHAN: $f (not referenced)"
  fi
done
```

### Step 1a: Reality Verification (CRITICAL)

**Check that `docs/0000a-IMMEDIATE-PLAN.md` matches actual state:**

```bash
# Compare plan against open issues
🤖 cat docs/0000a-IMMEDIATE-PLAN.md | grep -E "← CURRENT|In Progress|Next"
🤖 gh issue list --state open --repo martymcenroe/Aletheia --json number,title --jq '.[].number'
```

**Rule:** If the plan lists an issue as "Next" or "In Progress" that is NOT in the open issues list, flag as **Critical Staleness**.

| Check | Pass Condition |
|-------|----------------|
| Current Step issue is open | Issue number exists in `gh issue list --state open` |
| "In Progress" items are open | All listed issues exist in open state |
| Closed issues not shown as pending | No closed issues appear as "← CURRENT" |

### Step 2: CLAUDE.md / 0000-GUIDE.md Alignment

These two files must be consistent. Check:

| Check | CLAUDE.md | 0000-GUIDE.md |
|-------|-----------|---------------|
| Forbidden commands | Listed | Referenced |
| Workflow rules | Detailed | Summarized |
| Session log format | Referenced | Template in 0100 |
| Worktree protocol | Mandated | Explained |

```bash
# Quick diff of key sections
grep -A5 "Forbidden" CLAUDE.md
grep -A5 "Forbidden" docs/0000-GUIDE.md
```

### Step 3: Template Consistency

**Verify templates match their usage:**
```bash
# List all templates
ls docs/01*TEMPLATE*.md

# Check a sample report against template structure
# (Manual: compare docs/reports/*/implementation-report.md against 0103)
```

**Check template index (0100) lists all templates:**
```bash
for t in docs/01*TEMPLATE*.md; do
  basename="$(basename $t)"
  grep -q "$basename" docs/0100-TEMPLATE-GUIDE.md || echo "NOT IN INDEX: $t"
done
```

### Step 4: Protocol Executability

For each protocol (0009, 0004, etc.), verify:
- [ ] Steps are numbered and unambiguous
- [ ] Commands are copy-pasteable
- [ ] Expected outputs are documented
- [ ] Failure conditions are handled

**Quick check for incomplete protocols:**
```bash
# Protocols should have "## Procedure" or numbered steps
for p in docs/000[4-9]*.md docs/08*.md; do
  if ! grep -q -E "(## Procedure|### Step|### [SF][0-9])" "$p"; then
    echo "NO STEPS: $p"
  fi
done
```

### Step 5: Session Log Format Consistency

```bash
# Check recent session logs follow format
grep -c "^## [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}" docs/session-logs/*.md
```

### Step 6: Inventory Self-Check

```bash
# Verify 0003 lists itself and key system docs
for doc in 0000-GUIDE.md 0003-file-inventory.md CLAUDE.md; do
  grep -q "$doc" docs/0003-file-inventory.md || echo "NOT IN INVENTORY: $doc"
done
```

### Step 7: 0000-GUIDE Filing System Accuracy

**Verify all files listed in 0000-GUIDE.md §3 (Filing System) actually exist:**
```bash
# Extract filenames from 0000-GUIDE.md and check they exist
grep -oE '\`[0-9]{4}[a-z]?-[^`]+\.md\`' docs/0000-GUIDE.md | tr -d '\`' | while read f; do
  if [ ! -f "docs/$f" ] && [ ! -f "$f" ]; then
    echo "LISTED BUT MISSING: $f"
  fi
done
```

**Verify all 00xx/01xx docs are listed in 0000-GUIDE.md:**
```bash
# Check for undocumented standards
for f in docs/00[0-1][0-9]*.md; do
  basename="$(basename $f)"
  grep -q "$basename" docs/0000-GUIDE.md || echo "EXISTS BUT NOT LISTED: $basename"
done
```

**Action:** Update 0000-GUIDE.md §3 to include all current files.

## Auto-Fix (Default Behavior)

**This audit auto-fixes AssemblyZero health issues rather than just reporting them.**

### Auto-Fixable Items

| Finding | Auto-Fix Action |
|---------|-----------------|
| Broken doc reference | Update to correct path if target exists elsewhere |
| Missing from template index (0100) | Add entry to 0100-TEMPLATE-GUIDE.md |
| Missing from file inventory (0003) | Add entry to 0003-file-inventory.md |
| Missing from GUIDE filing system | Add entry to 0000-GUIDE.md §3 |
| Orphaned doc (exists but not listed) | Add to appropriate index |
| Stale IMMEDIATE-PLAN reference | Update or remove closed issue references |

### Auto-Fix Procedure

```markdown
For each auto-fixable finding:
1. Identify the target index/document
2. Generate the fix:
   - Template index: Add row with filename, purpose
   - File inventory: Add row with status, description
   - GUIDE filing system: Add to appropriate section
   - Broken reference: Update path to resolved target
3. Apply the edit
4. Log: "Auto-fixed: {description}"
```

### Cannot Auto-Fix

| Finding | Reason |
|---------|--------|
| CLAUDE.md / GUIDE alignment issues | Requires semantic judgment |
| Template drift | Old reports should not be updated |
| Unclear protocol steps | Requires human clarification |
| Conflicting guidance | Requires human decision on which is correct |
| Protocol executability issues | Requires domain expertise |

## Output Format

```markdown
## AssemblyZero Health Check - YYYY-MM-DD

### Auto-Fixed
- [x] Added `0107-TEMPLATE-xxx.md` to template index
- [x] Updated broken reference in 0004 from `0011.md` to `0007.md`

### Broken References (Unfixable)
- [ ] `docs/XXXX.md` references deleted `docs/YYYY.md` (target not found)

### Alignment Issues
- [ ] CLAUDE.md says X, 0000-GUIDE.md says Y

### Template Drift
- [ ] Template 0103 has section X, but reports lack it

### Protocol Issues
- [ ] Protocol 0009 step S3 has unclear expected output

### Recommendations
1. Fix broken reference in X
2. Align Y with Z
```

## Extended Analysis (Ultrathink Mode)

When invoked with extended thinking (ultrathink), perform deep analysis beyond the standard checks above. This mode is used for nightly audits and major system reviews.

See `docs/0901-runbook-nightly-assemblyzero-audit.md` for invocation instructions.

### Conflict Detection

Cross-reference all gate definitions across documents:
- Compare gates in CLAUDE.md vs 0000-GUIDE.md vs 0002 vs 0004
- Flag identical text blocks appearing in multiple files (redundancy)
- Identify contradictory instructions (conflict)

**What to look for:**
- Same gate defined differently in two places
- Rules that could never both be followed
- "SSOT violations" where multiple docs claim authority on same topic

### Redundancy Analysis

Find duplicate content that should be consolidated:
- >80% similar text blocks
- Alias skills/commands that add no value
- Stale staging directories with deployed content

**Action:** Recommend consolidation to SSOT

### Promotion Candidates

Identify recommendations that should become gates or hooks:
- Manual checklists that are frequently skipped
- Documentation-only gates that could be automated
- Rules in prose that could be enforced programmatically

**Promotion criteria:**
- Violation causes significant rework
- Automation is technically feasible
- Cost of enforcement < cost of violation

### Model Cost Analysis

Review model usage across audits:
- Flag Opus usage where Haiku/Sonnet would suffice
- Estimate savings from downgrades
- Note tasks that genuinely require Opus

**See:** `docs/0800-common-audits.md` for per-audit model recommendations

### Stale Content Detection

Find content that no longer reflects reality:
- IMMEDIATE-PLAN references to closed issues
- Index files out of sync with actual files
- Dead links to legacy or deleted documents
- Status indicators (🟢/🟡/🔴) that are outdated

## Issue Generation Workflow

After extended analysis, offer to batch-create GitHub issues for significant findings.

**Prompt:**
> "I found N significant findings. Would you like me to create GitHub issues for them?"

**Issue creation rules:**

| Finding Type | Requires Worktree | Branch to Main |
|--------------|-------------------|----------------|
| Code changes (.py, .js, .sh) | Yes | No |
| Hook modifications | Yes | No |
| Agent definition changes | Yes | No |
| Documentation-only fixes | No | Yes |

**Issue format:**
- Title: `[AssemblyZero] {finding type}: {brief description}`
- Label: `agentos`, `maintenance`
- Body: Include finding details, affected files, recommended fix

**Batch handling:**
- Create issues sequentially (avoid rate limits)
- Link related issues with "Related: #NNN"
- For documentation fixes, may combine multiple small fixes into one issue

## Integration

- Run as part of monthly maintenance
- Run before onboarding new AI agents
- **Nightly:** Run with ultrathink for deep analysis (see 0901)
- Results feed into system improvement issues

## Common Findings

| Finding | Cause | Fix |
|---------|-------|-----|
| Broken doc reference | Renumbering without updating refs | grep + sed |
| Template drift | Template updated, old reports not | Accept drift in old reports |
| Conflicting guidance | Multiple authors, no review | Consolidate into one source |
| Unclear protocol step | Written for expert, not novice | Add expected output |

## History

| Date | Change |
|------|--------|
| 2026-01-04 | Created. |
