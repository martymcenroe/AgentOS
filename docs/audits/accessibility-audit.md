# Accessibility Audit

Generic accessibility audit framework based on WCAG 2.1 AA standards.

## 1. Purpose

Accessibility audit covering perceivable, operable, understandable, and robust (POUR) principles. Based on:
- WCAG 2.1 Level AA
- Section 508
- EN 301 549

---

## 2. WCAG 2.1 Checklist

### Perceivable

| Criterion | Requirement | Status |
|-----------|-------------|--------|
| 1.1.1 | Non-text content has text alternatives | |
| 1.2.1 | Audio/video has captions or transcript | |
| 1.3.1 | Information structure conveyed programmatically | |
| 1.4.1 | Color not sole means of conveying info | |
| 1.4.3 | Text contrast ratio ≥ 4.5:1 | |
| 1.4.4 | Text resizable to 200% without loss | |

### Operable

| Criterion | Requirement | Status |
|-----------|-------------|--------|
| 2.1.1 | All functionality keyboard accessible | |
| 2.1.2 | No keyboard traps | |
| 2.2.1 | Timing adjustable or extendable | |
| 2.3.1 | No flashing content >3 times/sec | |
| 2.4.1 | Skip navigation mechanism | |
| 2.4.3 | Focus order logical and meaningful | |
| 2.4.4 | Link purpose clear from context | |

### Understandable

| Criterion | Requirement | Status |
|-----------|-------------|--------|
| 3.1.1 | Page language programmatically set | |
| 3.2.1 | No unexpected context changes on focus | |
| 3.2.2 | No unexpected context changes on input | |
| 3.3.1 | Input errors identified and described | |
| 3.3.2 | Labels/instructions for user input | |

### Robust

| Criterion | Requirement | Status |
|-----------|-------------|--------|
| 4.1.1 | Valid HTML (no parsing errors) | |
| 4.1.2 | ARIA used correctly | |

---

## 3. Manual Testing Checklist

### Keyboard Navigation

| Test | Expected | Status |
|------|----------|--------|
| Tab through all interactive elements | All reachable | |
| Focus visible on all elements | Clear indicator | |
| No focus traps | Can escape any component | |
| Skip links work | Jump to main content | |

### Screen Reader Testing

| Test | Expected | Status |
|------|----------|--------|
| Page title announced | Descriptive title | |
| Headings structure logical | H1→H2→H3 hierarchy | |
| Images have alt text | Meaningful descriptions | |
| Form labels announced | Clear input purpose | |
| Error messages announced | Clear error description | |

### Color & Contrast

| Element | Required Ratio | Actual | Status |
|---------|----------------|--------|--------|
| Body text | 4.5:1 | | |
| Large text | 3:1 | | |
| UI components | 3:1 | | |
| Focus indicator | 3:1 | | |

---

## 4. ARIA Guidelines

### Required Attributes

| Element | Required ARIA |
|---------|---------------|
| Custom buttons | role="button", aria-pressed |
| Dialogs | role="dialog", aria-modal, aria-labelledby |
| Tabs | role="tablist", role="tab", aria-selected |
| Alerts | role="alert" or aria-live |

### Common Mistakes

| Mistake | Correct Approach |
|---------|------------------|
| Using ARIA when native works | Use `<button>` not `<div role="button">` |
| Missing accessible names | Add aria-label or aria-labelledby |
| Incorrect role | Use appropriate semantic role |
| aria-hidden on focusable | Remove from tab order first |

---

## 5. Automated Testing Tools

| Tool | Purpose |
|------|---------|
| axe DevTools | Browser extension for WCAG scanning |
| WAVE | Web accessibility evaluation |
| Lighthouse | Chrome DevTools accessibility audit |
| pa11y | CLI accessibility testing |

### Integration

```bash
# Example: pa11y in CI
pa11y --standard WCAG2AA https://example.com
```

---

## 6. Audit Procedure

1. Run automated scanning tools
2. Perform keyboard navigation test
3. Test with screen reader
4. Check color contrast
5. Review ARIA usage
6. Document findings
7. Create remediation plan

---

## 7. Output Format

```markdown
# Accessibility Audit Report: {DATE}

## Summary
- WCAG Level: AA
- Issues Found: {count}
- Automated Score: {X}%

## WCAG Checklist
| Criterion | Status | Notes |
|-----------|--------|-------|
| 1.1.1 | ✅ | All images have alt |
| 1.4.3 | ⚠️ | Low contrast on footer |

## Manual Testing
| Test | Status | Notes |
|------|--------|-------|
| Keyboard nav | ✅ | All elements reachable |
| Screen reader | ⚠️ | Missing form labels |

## Findings
| ID | Severity | WCAG | Finding | Remediation |
|----|----------|------|---------|-------------|
| A1 | High | 1.4.3 | Low contrast | Increase to 4.5:1 |

## Recommendations
1. ...
2. ...
```

---

## 8. References

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM Checklist](https://webaim.org/standards/wcag/checklist)
- [MDN Accessibility Guide](https://developer.mozilla.org/en-US/docs/Web/Accessibility)

---

*Source: AgentOS/docs/audits/accessibility-audit.md*
*Project-specific accessibility requirements extend this framework.*
