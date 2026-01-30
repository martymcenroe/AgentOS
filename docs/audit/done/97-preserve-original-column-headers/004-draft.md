# Preserve Original Column Headers in CSV Output

## User Story
As a **core analysis data consumer**,
I want **CSV output to preserve the exact column headers from the source PDF**,
So that **the output matches the original document format as required by the assignment**.

## Objective
Update CSV generation to use original PDF column headers verbatim instead of programmer-friendly canonical names, while maintaining security through formula injection protection.

## UX Flow

### Scenario 1: Standard PDF Extraction
1. User runs extraction on `W20552.pdf`
2. System detects headers like "Sample No.", "Depth (ft)", "Permeability (md) Air"
3. System outputs CSV with those exact headers preserved
4. Result: CSV headers match PDF headers exactly

### Scenario 2: Headers with Special Characters
1. User runs extraction on PDF with headers containing parentheses, units, symbols
2. System preserves "Porosity (%) Ambient" exactly as written
3. Result: Original text preserved with CSV-safe escaping applied

### Scenario 3: Multi-line Headers (Post-004 Flattening)
1. User runs extraction after 004 has flattened multi-row headers
2. System receives flattened header like "Permeability (md) Air"
3. System uses the flattened original text (not canonical name)
4. Result: Output reflects the logical header from the PDF structure

### Scenario 4: Headers with Formula Characters
1. User runs extraction on PDF with header starting with `=`, `@`, `+`, or `-`
2. System detects formula injection risk
3. System prepends `'` to escape the leading character
4. Result: Header preserved but safe from CSV injection when opened in Excel

### Scenario 5: Headers with Delimiters or Newlines
1. User runs extraction on PDF with header containing commas or newlines
2. System applies standard CSV quoting per RFC 4180
3. Result: Header text preserved exactly, properly quoted for CSV format

## Requirements

### Header Preservation
1. CSV headers must use exact text from PDF table headers
2. Original whitespace, parentheses, and units must be preserved
3. No snake_case conversion or programmatic renaming in output
4. Standard CSV escaping (quoting) must be applied for headers containing delimiters (commas) or newlines, handled via Python's `csv.QUOTE_MINIMAL`

### Security: CSV Injection Protection
1. Headers starting with formula characters (`=`, `@`, `+`, `-`) must be escaped by prepending `'`
2. This protection applies to header text only after original text capture
3. Escaping prevents code execution when CSV opened in spreadsheet applications

### Data Processing Environment
1. All PDF processing must occur locally on the user's machine
2. No external API transmission of PDF contents permitted
3. Processing environment: Local-Only

### Dual-Header Architecture
1. Maintain `original_headers` for CSV output
2. Maintain `canonical_headers` for internal code access
3. Row data keyed by canonical names for programmatic convenience

### Output Format
1. First row of CSV contains original headers (with security escaping applied)
2. Headers appear in same order as PDF table
3. No additional header rows or metadata rows

## Technical Approach
- **Table dataclass:** Add `original_headers: list[str]` field alongside existing canonical headers
- **Header extraction (004):** Capture original text before any normalization
- **CSV injection protection:** Apply formula character escaping before CSV output
- **CSV writer:** Use `table.original_headers` for `writerow()` with `csv.QUOTE_MINIMAL` for proper delimiter handling
- **Row access:** Continue using canonical keys internally for clean code

## Security Considerations
- **CSV Injection Prevention:** Headers starting with `=`, `@`, `+`, `-` are escaped with leading `'` to prevent formula execution in Excel/Sheets
- **Local Processing Only:** All PDF parsing occurs locally; no data transmitted to external services
- **Standard CSV Escaping:** Using Python's csv module with `QUOTE_MINIMAL` handles embedded delimiters safely

## Files to Create/Modify
- `src/models/table.py` — Add `original_headers` field to Table dataclass
- `src/extraction/header_extractor.py` — Store original text during header detection
- `src/output/csv_writer.py` — Use original headers in output generation with formula injection protection
- `src/output/csv_sanitizer.py` — New module for CSV injection escaping logic
- `tests/test_header_preservation.py` — New test file for header preservation
- `tests/test_csv_injection_protection.py` — New test file for security escaping

## Dependencies
- Issue #004 must be completed first (header detection and multi-row flattening)
- **Action Required:** Verify #004 is in "Done" state before starting this issue

## Out of Scope (Future)
- Header translation/mapping configuration — deferred
- Multiple output format support (JSON, Excel) — separate issue
- Header validation against known schemas — future enhancement

## Acceptance Criteria
- [ ] CSV output contains headers matching PDF exactly (e.g., "Depth (ft)" not "depth_feet")
- [ ] No canonical/snake_case names appear in CSV header row
- [ ] Original units preserved in headers (e.g., "(md)", "(%)", "(ft)")
- [ ] Original punctuation preserved (e.g., "Sample No." with period)
- [ ] Headers with formula characters (`=`, `@`, `+`, `-`) are escaped with leading `'`
- [ ] Headers containing commas or newlines are properly quoted per CSV standard
- [ ] Internal code can still access data via canonical keys
- [ ] All PDF processing occurs locally with no external API calls

## Definition of Done

### Implementation
- [ ] Table dataclass updated with original_headers field
- [ ] Header extraction captures original text
- [ ] CSV injection protection implemented and tested
- [ ] CSV writer uses original headers with proper escaping
- [ ] Unit tests written and passing

### Tools
- [ ] Verify extraction CLI outputs correct headers
- [ ] Manual spot-check against source PDF

### Documentation
- [ ] Update data model documentation with dual-header approach
- [ ] Document header preservation requirement in README
- [ ] Document CSV injection protection in security notes
- [ ] Add new files to `docs/0003-file-inventory.md`

### Reports (Pre-Merge Gate)
- [ ] `docs/reports/005/implementation-report.md` created
- [ ] `docs/reports/005/test-report.md` created

### Verification
- [ ] Output CSV headers match PDF headers exactly (with security escaping)
- [ ] All existing tests still pass
- [ ] Run 0809 Security Audit - PASS (CSV injection protection)

## Testing Notes

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

def test_dual_header_access():
    """Verify code can access data via canonical keys."""
    table = extract_table("W20552.pdf")
    
    # Original preserved for output
    assert "Depth (ft)" in table.original_headers
    
    # Canonical available for code
    assert "depth_feet" in table.canonical_headers
    
    # Row access works via canonical
    row = table.rows[0]
    assert row["depth_feet"] == 9580.5

def test_formula_injection_escaped():
    """Verify headers starting with formula chars are escaped."""
    # Simulate header that starts with '='
    sanitized = sanitize_header("=SUM(A1)")
    assert sanitized == "'=SUM(A1)"
    
    # Test all formula characters
    assert sanitize_header("@mention") == "'@mention"
    assert sanitize_header("+value") == "'+value"
    assert sanitize_header("-negative") == "'-negative"
    
    # Normal headers unchanged
    assert sanitize_header("Depth (ft)") == "Depth (ft)"

def test_headers_with_delimiters():
    """Verify headers with commas are properly quoted."""
    result = extract_to_csv(pdf_with_comma_header)
    
    with open(result) as f:
        content = f.read()
    
    # Header with comma should be quoted
    assert '"Permeability, Air"' in content or 'Permeability, Air' in content
```

To force error states:
- Test with headers containing commas (CSV escaping)
- Test with headers containing quotes
- Test with empty/missing headers in source PDF
- Test with headers starting with `=`, `@`, `+`, `-` (formula injection)
- Test with headers containing newline characters

## Labels
`feature`, `data-integrity`, `priority:medium`

## Effort Estimate
**Size:** S/M (Small to Medium)