# 0844 - File Inventory Drift Audit

**Status:** STUB - Implementation pending
**Category:** Documentation Health
**Frequency:** Weekly
**Auto-Fix:** Yes (can regenerate inventory)

---

## Purpose

Keep `docs/0003-file-inventory.md` synchronized with actual files. The inventory is useless if it lies.

---

## Checks

### 1. Count Validation

| Category | Inventory Says | Glob Finds | Status |
|----------|----------------|------------|--------|
| Standards | 9 | `glob docs/standards/*.md` | MATCH/DRIFT |
| Templates | 10 | `glob docs/templates/*.md` | MATCH/DRIFT |
| Audits | 28 | `glob docs/audits/*.md` | MATCH/DRIFT |
| Tools | 12 | `glob tools/*.py` | MATCH/DRIFT |
| Commands | 9 | `glob .claude/commands/*.md` | MATCH/DRIFT |

**Suggested implementation:**
```python
inventory_counts = parse_inventory("docs/0003-file-inventory.md")
actual_counts = {
    "standards": len(glob("docs/standards/*.md")),
    "templates": len(glob("docs/templates/*.md")),
    # ...
}
for category, expected in inventory_counts.items():
    actual = actual_counts[category]
    if expected != actual:
        print(f"DRIFT: {category} inventory={expected} actual={actual}")
```

### 2. File Listing Accuracy

Beyond counts, verify each listed file exists:
- Parse table rows from inventory
- Check each file path exists
- Flag: listed but missing, exists but unlisted

### 3. Status Accuracy

Inventory marks files as "Stable", "Beta", "In-Progress". Verify:
- "Stable" files have tests
- "Stable" files have documentation
- "In-Progress" files are actually being worked on (recent commits)
- "Beta" files aren't actually stable (been unchanged for weeks)

### 4. Orphan Detection

Files that exist but are in NO documentation:
- Not in inventory
- Not in index
- Not referenced by any other doc

These are documentation black holes.

### 5. Numbering Conflicts

Detect duplicate numbers across categories:
- Two files with same 0XXX prefix
- Files with numbers outside their category range

---

## Auto-Fix Capability

1. **Regenerate counts** from actual glob results
2. **Add missing files** to appropriate tables
3. **Flag removed files** for human decision (delete row or investigate)
4. **Cannot auto-fix** status (requires judgment)

---

## Suggestions for Future Implementation

1. **Inventory Generation Tool**: `python tools/generate-inventory.py` that rebuilds the entire inventory from scratch.

2. **Commit Hook**: Pre-commit check that inventory matches reality.

3. **Category Validation**: Ensure files are in correct category based on number (00xx = standards, 01xx = templates, etc.)

4. **Cross-Index Validation**: Verify inventory matches `docs/index.md` matches actual files.

5. **Last-Modified Tracking**: Add "last modified" column to inventory, auto-update from git.

---

## Audit Record

| Date | Auditor | Findings | Issues Created |
|------|---------|----------|----------------|
| - | - | STUB - Not yet implemented | - |

---

## Related

- [0003 - File Inventory](../0003-file-inventory.md)
- [0838 - Broken References](0838-audit-broken-references.md)
