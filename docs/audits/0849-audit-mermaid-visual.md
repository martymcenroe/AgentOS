# 0849 - Mermaid Diagram Visual Audit

## Purpose

Verify that all Mermaid diagrams across all repositories render correctly on GitHub in both light and dark mode. Catches:
- **Lines behind boxes** — edges routing through or behind node boxes (§8.3)
- **Dark mode contrast failures** — custom fill colors invisible on dark backgrounds (§8.6)
- **Edge label illegibility** — gray-on-gray text in dark mode (§8.6)
- **Cyclic flow layout problems** — backward edges causing crossing lines (§7.4)
- **Touching/overlapping elements** — nodes or subgraphs colliding (§8.2)
- **Truncated labels** — text cut off by narrow boxes
- **Broken rendering** — mermaid syntax errors producing error blocks instead of diagrams

## Trigger

- Monthly (part of full audit suite)
- After creating or modifying mermaid diagrams
- After mermaid standards (0004) updates

## Standards Reference

All checks are against [0004 - Mermaid Diagram Standards](../standards/0004-mermaid-diagrams.md):

| Section | Rule |
|---------|------|
| §7.0 | Dagre layout awareness |
| §7.4 | Cyclic flow handling |
| §8.1 | Simplicity principle |
| §8.2 | No touching elements |
| §8.3 | No lines behind boxes |
| §8.4 | Visual inspection checklist |
| §8.6 | Dark mode compatibility |
| §8.7 | Playwright-based inspection |

---

## Procedure

### Step 1: Discover Mermaid Diagrams

Find all mermaid code blocks across all repos.

**Local repos (fast, complete):**

```bash
# Search all local repos for mermaid blocks
for dir in /c/Users/mcwiz/Projects/*/; do
    count=$(grep -rl '```mermaid' "$dir" --include="*.md" 2>/dev/null | wc -l)
    if [ "$count" -gt 0 ]; then
        echo "$count  $(basename "$dir")"
        grep -rl '```mermaid' "$dir" --include="*.md" 2>/dev/null
    fi
done
```

**Wiki repos (cloned locally as `*-wiki` or `*.wiki`):**

```bash
# Check wiki clones
for dir in /c/Users/mcwiz/Projects/*wiki* /c/Users/mcwiz/Projects/*.wiki; do
    if [ -d "$dir" ]; then
        count=$(grep -rl '```mermaid' "$dir" --include="*.md" 2>/dev/null | wc -l)
        if [ "$count" -gt 0 ]; then
            echo "$count  $(basename "$dir")"
            grep -rl '```mermaid' "$dir" --include="*.md" 2>/dev/null
        fi
    fi
done
```

**Output:** A manifest of every file containing mermaid diagrams, organized by repo.

### Step 2: Determine GitHub URLs

For each file with mermaid diagrams, construct the GitHub URL where it renders:

| Source | URL Pattern |
|--------|------------|
| README.md | `https://github.com/martymcenroe/{repo}` |
| Wiki page | `https://github.com/martymcenroe/{repo}/wiki/{page-name}` |
| Other .md in repo | `https://github.com/martymcenroe/{repo}/blob/main/{path}` |
| ADR / docs | `https://github.com/martymcenroe/{repo}/blob/main/docs/{path}` |

**Private repos:** Playwright must be authenticated (logged into GitHub) to access private repo pages. If not authenticated, document these as "cannot inspect — private repo, not authenticated."

### Step 3: Visual Inspection via Playwright

For each page containing mermaid diagrams:

1. **Navigate** to the GitHub URL
2. **Wait** for mermaid rendering (iframes load asynchronously)
3. **Screenshot in current mode** (light or dark depending on GitHub settings)
4. **Switch theme** via GitHub Settings > Appearance
5. **Screenshot in other mode**
6. **Inspect both screenshots** against the checklist below

**Important:** GitHub renders mermaid in `<iframe>` elements. The Playwright `browser_snapshot` (accessibility tree) returns `[iframe]` placeholders and cannot read diagram content. **Screenshots are the only inspection method.**

### Step 4: Per-Diagram Checklist

For each mermaid diagram, verify:

| # | Check | Standard | Method |
|---|-------|----------|--------|
| 1 | All arrows visible (not behind boxes) | §8.3 | Visual — both modes |
| 2 | No overlapping/touching elements | §8.2 | Visual — both modes |
| 3 | All labels readable (not truncated) | §8.4 | Visual — both modes |
| 4 | Edge labels legible in dark mode | §8.6 | Visual — dark mode |
| 5 | Custom fill colors visible in both modes | §8.6 | Visual — compare modes |
| 6 | No backward edges crossing through nodes | §7.4 | Visual — both modes |
| 7 | Flow direction clear | §8.4 | Visual — both modes |
| 8 | Subgraph boundaries don't cut elements | §8.4 | Visual — both modes |
| 9 | Diagram renders (no error block) | §5.x | Visual — either mode |
| 10 | Uses TD layout (not LR with backward edges) | §4, §7.1 | Source review |

### Step 5: Record Findings

For each diagram, record:

```markdown
### {Repo} / {File} — Diagram {N}

| Check | Light | Dark | Notes |
|-------|-------|------|-------|
| Arrows visible | PASS/FAIL | PASS/FAIL | |
| No overlapping | PASS/FAIL | PASS/FAIL | |
| Labels readable | PASS/FAIL | PASS/FAIL | |
| Edge labels legible | — | PASS/FAIL | |
| Fill colors visible | PASS/FAIL | PASS/FAIL | |
| No crossing backward edges | PASS/FAIL | PASS/FAIL | |
| Flow direction clear | PASS/FAIL | PASS/FAIL | |
| Subgraph boundaries clean | PASS/FAIL | PASS/FAIL | |
| Renders correctly | PASS/FAIL | PASS/FAIL | |
| TD layout compliance | PASS/FAIL | PASS/FAIL | |
```

### Step 6: Fix or File Issues

Per the Fix-First Mandate (0800 §2.3):

1. **Auto-fix immediately** if the diagram is in a repo you have write access to and the fix is straightforward (remove backward edge, adjust fill colors, quote labels)
2. **Create GitHub issue** in the diagram's repo if the fix requires design decisions or the repo is not writable
3. **Document exception** only if fix is impossible (e.g., upstream mermaid rendering bug)

---

## Scope: Repos to Audit

### Public Repos with Wikis (highest priority — visible to everyone)

| Repo | Wiki | README | Other .md |
|------|------|--------|-----------|
| AssemblyZero | Check | Check | docs/standards/, docs/audits/ |
| Aletheia | Check | Check | docs/ |
| unleashed | Check | Check | docs/adrs/ |
| Clio | Check | Check | |
| RCA-PDF-extraction-pipeline | Check | Check | |
| ai-power-systems-compendium | Check | Check | |
| best-of-pes-ai | Check | Check | |
| automation-scripts | Check | Check | |
| gh-link-auditor | Check | Check | |
| iconoscope | Check | Check | |
| martymcenroe | Check | Check | |
| martymcenroe.github.io | Check | Check | |
| metabolic-protocols | Check | Check | |
| nec2017-analyzer | Check | Check | |
| power-agent.github.io | Check | Check | |
| thrivetech-ai | Check | Check | |
| dotfiles | Check | Check | |
| athleet.github.io | Check | Check | |
| my-discussions | Check | Check | |
| GlucoPulse | — | Check | |

### Private Repos (audit if authenticated)

| Repo | Wiki | README |
|------|------|--------|
| Talos | — | Check |
| career | — | Check |
| dispatch | — | Check |
| maintenance | — | Check |
| GentlePersuader | Check | Check |
| CS512_link_predictor | Check | Check |
| TheMobyPerogative.world | Check | Check |
| Agora | — | Check |
| job-sniper | — | Check |
| Others (see full repo list) | — | Check |

### Cannot Inspect via Playwright

Document any repos where Playwright cannot access the page:
- Private repos without authentication
- Repos with empty wikis (no pages)
- Pages behind additional auth (e.g., GitHub Enterprise)

---

## Model Recommendation

**Sonnet** — Requires visual inspection (multimodal) but checks are structured. Haiku lacks the visual reasoning needed for diagram quality assessment.

## Frequency

**Monthly** — Mermaid diagrams change infrequently but standards evolve. Monthly catches drift.

## Dependencies

- Requires updated 0004 Mermaid Diagram Standards (§7.0, §7.4, §8.6, §8.7)
- Requires Playwright MCP server connected and browser available
- Requires GitHub authentication for private repos

---

## Audit Record

| Date | Auditor | Scope | Findings Summary | Issues Created |
|------|---------|-------|------------------|----------------|
| 2026-02-15 | Claude Opus 4.6 | All repos (14 with mermaid, ~94 diagrams) | 5 violations (3 LR+backward, 1 pastel dark mode, 1 LR+backward), 2 potential issues | Pending (7 actions) |
