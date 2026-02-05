# 0826 - Cross-Browser Testing Audit

**Status:** [Under Development]
**Created:** 2026-02-05
**Frequency:** On release, monthly for active extensions

---

## Purpose

Verify browser extensions work consistently across Chrome and Firefox, with file parity and mock fidelity.

---

## Scope

This audit applies to projects with browser extensions:
- Chrome extensions (Manifest V3)
- Firefox add-ons (WebExtensions API)
- Cross-browser compatibility layers

**Primary consumer:** Aletheia (Chrome extension with Firefox support planned)

---

## Checklist (Draft)

### File Parity
- [ ] manifest.json exists for both browsers (or uses browser-specific builds)
- [ ] All JavaScript files present in both builds
- [ ] CSS/assets identical or browser-specific variants documented

### Mock Fidelity
- [ ] Unit tests use mocks that match real browser APIs
- [ ] chrome.* API mocks match actual behavior
- [ ] browser.* polyfill works correctly in Firefox

### Functional Testing
- [ ] Extension loads without errors in Chrome
- [ ] Extension loads without errors in Firefox
- [ ] Core functionality works in both browsers
- [ ] Popup UI renders correctly in both

### Known Divergences
- [ ] Document any browser-specific code paths
- [ ] Document features that work differently per browser

---

## Implementation Notes

**Not yet implemented.** This audit was identified during Issue #19 (audit reorganization) as a useful framework for browser extension projects.

To implement:
1. Create automated test scripts for extension loading
2. Add browser-specific manifest validation
3. Create mock fidelity checker tool

---

## Audit Record

| Date | Auditor | Findings | Issues |
|------|---------|----------|--------|
| - | - | Not yet executed | - |
