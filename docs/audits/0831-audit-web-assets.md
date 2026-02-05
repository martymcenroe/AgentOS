# 0831 - Web Assets Audit

**Status:** [Under Development]
**Created:** 2026-02-05
**Frequency:** Monthly, on UI changes

---

## Purpose

Verify web assets (HTML, CSS, images) meet quality standards for visual design, responsiveness, and accessibility.

---

## Scope

This audit applies to projects with web UI:
- Browser extension popups and options pages
- Web applications
- Landing pages
- Admin dashboards

**Primary consumer:** Aletheia (extension popup UI)

---

## Checklist (Draft)

### Visual Design
- [ ] Consistent color scheme (matches brand)
- [ ] Typography hierarchy clear (headings, body, captions)
- [ ] Spacing/margins consistent
- [ ] Icons/images appropriate resolution
- [ ] No placeholder content in production

### Responsive Design
- [ ] Layout works at minimum popup size (300px wide)
- [ ] Layout works at maximum popup size
- [ ] Text doesn't overflow containers
- [ ] Buttons/controls have adequate touch targets
- [ ] Scrolling behavior appropriate

### Performance
- [ ] Images optimized (WebP, appropriate compression)
- [ ] CSS minified in production
- [ ] No unused CSS (tree-shaking)
- [ ] Critical CSS inlined if needed
- [ ] Total asset size reasonable

### Accessibility (Cross-reference with 0804)
- [ ] Color contrast meets WCAG AA
- [ ] Focus indicators visible
- [ ] Alt text on images
- [ ] Keyboard navigation works
- [ ] Screen reader compatible

### Browser Compatibility
- [ ] Works in Chrome (latest)
- [ ] Works in Firefox (latest)
- [ ] Works in Edge (latest)
- [ ] Graceful degradation for older browsers

---

## Implementation Notes

**Not yet implemented.** This audit was identified during Issue #19 (audit reorganization) as a useful framework for web UI projects.

To implement:
1. Create Lighthouse CI integration
2. Add visual regression testing (Percy, Chromatic)
3. Create responsive breakpoint checker
4. Add accessibility scanner (axe-core)

**Recommended model:** Sonnet (visual design evaluation requires moderate reasoning)

---

## Audit Record

| Date | Auditor | Findings | Issues |
|------|---------|----------|--------|
| - | - | Not yet executed | - |
