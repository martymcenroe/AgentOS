# 0828 - Build Artifact Freshness Audit

**Status:** [Under Development]
**Created:** 2026-02-05
**Frequency:** Weekly, on release

---

## Purpose

Verify build outputs are current and match source code - no stale artifacts being deployed.

---

## Scope

This audit applies to projects with build artifacts:
- Browser extension packages (.crx, .xpi, .zip)
- Lambda deployment packages (.zip)
- Docker images
- Compiled binaries
- Bundled JavaScript (webpack, rollup output)

**Primary consumer:** Aletheia (extension builds, Lambda packages)

---

## Checklist (Draft)

### Source-to-Artifact Freshness
- [ ] Build artifacts newer than source files
- [ ] No uncommitted source changes that aren't in artifacts
- [ ] Version numbers in artifacts match package.json/pyproject.toml

### Extension Packages
- [ ] manifest.json version matches release tag
- [ ] All source files included in package
- [ ] No development-only files in production package
- [ ] Package size reasonable (no bloat)

### Lambda Packages
- [ ] requirements.txt/pyproject.toml dependencies included
- [ ] No dev dependencies in production package
- [ ] Handler paths correct
- [ ] Package under Lambda size limits

### Docker Images
- [ ] Image tag matches release version
- [ ] Base image reasonably current
- [ ] No secrets baked into image
- [ ] Multi-stage build used (no build tools in prod image)

### Timestamp Verification
- [ ] CI/CD timestamp recorded in artifact
- [ ] Git commit SHA embedded in build
- [ ] Build reproducible from recorded commit

---

## Implementation Notes

**Not yet implemented.** This audit was identified during Issue #19 (audit reorganization) as a useful framework for projects with build pipelines.

To implement:
1. Create timestamp comparison scripts
2. Add build metadata extraction tools
3. Create package content validators

---

## Audit Record

| Date | Auditor | Findings | Issues |
|------|---------|----------|--------|
| - | - | Not yet executed | - |
