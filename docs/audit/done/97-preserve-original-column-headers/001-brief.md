# Idea: Preserve Original Column Headers

**Status:** Blocker (missed requirement)
**Effort:** Low (1-2 hours)
**Value:** Critical - core assignment requirement
**Blocked by:** 004 (header normalization must detect headers first)

---

## Problem

The assignment explicitly requires: "You must preserve column headers."

Current implementation invents column names:

| PDF Header | CSV Header (current) |
|------------|---------------------|
| Sample No. | sample_number |
| Depth (ft) | depth_feet |
| Permeability (md) Air | permeability_air_md |
| Porosity (%) Ambient | porosity_ambient_pct |

This violates the requirement. The CSV should use the **exact** headers from the PDF.

---

## Current Output

```csv
core_number,sample_number,depth_feet,permeability_air_md,...
4,6-1,9580.5,0.042,...
```

## Required Output

```csv
Core,Sample No.,Depth (ft),Permeability (md) Air,...
4,6-1,9580.5,0.042,...
```

---

## Root Cause

The `core_analysis_minimal.csv` was hand-crafted with programmer-friendly column names. No automated header extraction was performed - headers were guessed from context.

---

## Proposal

1. Extract actual headers from PDF tables (depends on 004)
2. Use extracted headers verbatim in CSV output
3. Preserve original formatting, units, whitespace

---

## Implementation

After 004 (header normalization) extracts and flattens headers:

```python
def build_csv_with_original_headers(table: Table) -> str:
    """Build CSV using original PDF headers, not canonical names."""

    # table.original_headers = ["Core", "Sample No.", "Depth (ft)", ...]
    # table.canonical_headers = ["core_number", "sample_number", "depth_feet", ...]

    writer = csv.writer(output)
    writer.writerow(table.original_headers)  # Use original, not canonical

    for row in table.rows:
        writer.writerow(row.values())

    return output.getvalue()
```

---

## Dual-Header Approach

For internal processing, maintain both:

```python
@dataclass
class Table:
    original_headers: list[str]   # "Permeability (md) Air" - for output
    canonical_headers: list[str]  # "permeability_air_md" - for code access
    rows: list[dict]              # Keyed by canonical for easy access
```

This allows:
- **Output:** Original headers preserved per requirement
- **Code:** Clean programmatic access via canonical names

---

## Deliverable

Update CSV output to use original PDF headers exactly as they appear in the document.

---

## Testing

```python
def test_original_headers_preserved():
    """Verify CSV uses original PDF headers."""
    result = extract_to_csv("W20552.pdf")

    with open(result) as f:
        reader = csv.reader(f)
        headers = next(reader)

    # Should contain original PDF text, not canonical names
    assert "Depth (ft)" in headers or "Depth" in headers
    assert "depth_feet" not in headers

    assert "Sample" in headers or "Sample No." in headers
    assert "sample_number" not in headers
```

---

## Next Steps

1. [ ] Wait for 004 (header detection/extraction)
2. [ ] Capture original header text during extraction
3. [ ] Update CSV writer to use original headers
4. [ ] Verify output matches PDF headers exactly
