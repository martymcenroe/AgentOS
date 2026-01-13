# Code Quality Audit

Generic code quality audit framework based on software engineering best practices.

## 1. Purpose

Code quality audit covering maintainability, complexity, and consistency. Based on:
- SOLID Principles
- Clean Code practices
- Complexity metrics
- Code review standards

---

## 2. SOLID Principles Checklist

| Principle | Check | Status |
|-----------|-------|--------|
| **Single Responsibility** | Each class/function has one job | |
| **Open/Closed** | Open for extension, closed for modification | |
| **Liskov Substitution** | Subtypes can replace base types | |
| **Interface Segregation** | No forced dependency on unused methods | |
| **Dependency Inversion** | Depend on abstractions, not concretions | |

---

## 3. Complexity Metrics

### Cyclomatic Complexity

| Score | Rating | Action |
|-------|--------|--------|
| 1-10 | Low | Acceptable |
| 11-20 | Moderate | Review for simplification |
| 21-50 | High | Refactor recommended |
| 50+ | Critical | Must refactor |

### Measurement

```bash
# Python
radon cc src/ -a -s

# JavaScript
npx complexity-report src/
```

### File/Function Size

| Metric | Guideline |
|--------|-----------|
| Function length | <50 lines |
| File length | <500 lines |
| Class methods | <20 methods |
| Parameters | <5 parameters |

---

## 4. Code Consistency

### Linting

| Language | Tool | Status |
|----------|------|--------|
| Python | Ruff/Flake8 | |
| JavaScript | ESLint | |
| TypeScript | ESLint + TSC | |

### Formatting

| Language | Tool | Status |
|----------|------|--------|
| Python | Black/Ruff | |
| JavaScript | Prettier | |
| All | EditorConfig | |

### Type Safety

| Check | Requirement |
|-------|-------------|
| Type hints (Python) | All public functions |
| TypeScript strict | strictNullChecks enabled |
| No `any` abuse | Specific types used |

---

## 5. Test Coverage

| Category | Target | Actual |
|----------|--------|--------|
| Unit tests | 80% | |
| Critical paths | 100% | |
| Edge cases | 90% | |

### Coverage Tools

```bash
# Python
pytest --cov=src --cov-report=html

# JavaScript
jest --coverage
```

---

## 6. Documentation Quality

### Code Documentation

| Check | Requirement |
|-------|-------------|
| Public API | Docstrings/JSDoc for all |
| Complex logic | Explanatory comments |
| Dependencies | Clear import organization |

### Project Documentation

| Check | Requirement |
|-------|-------------|
| README | Setup and usage instructions |
| API docs | Endpoint/interface documentation |
| Architecture | System overview and decisions |

---

## 7. Dead Code Detection

### Signs of Dead Code

- Unused imports
- Unreachable code paths
- Commented-out code
- Unused functions/classes
- TODO comments without issues

### Tools

```bash
# Python
vulture src/

# JavaScript
npx unimported
```

---

## 8. Dependency Health

| Check | Requirement |
|-------|-------------|
| Lock files | Committed and up-to-date |
| Outdated packages | Review quarterly |
| Unused dependencies | Remove |
| Circular dependencies | None |

---

## 9. Audit Procedure

1. Run linting tools
2. Calculate complexity metrics
3. Check test coverage
4. Review documentation
5. Scan for dead code
6. Check dependencies
7. Document findings
8. Create remediation plan

---

## 10. Output Format

```markdown
# Code Quality Audit Report: {DATE}

## Summary
- Linting: {PASS/FAIL}
- Avg Complexity: {score}
- Test Coverage: {%}
- Documentation: {%}

## Complexity Hot Spots
| File | Function | Complexity |
|------|----------|------------|
| | | |

## Linting Issues
| Category | Count | Sample |
|----------|-------|--------|
| | | |

## Coverage Gaps
| File | Coverage | Critical? |
|------|----------|-----------|
| | | |

## Findings
| ID | Severity | Category | Finding | Remediation |
|----|----------|----------|---------|-------------|
| Q1 | Medium | Complexity | Function X has CC=25 | Split into helpers |

## Recommendations
1. ...
2. ...
```

---

## 11. References

- Clean Code (Robert C. Martin)
- SOLID Principles
- Cyclomatic Complexity (Thomas McCabe)

---

*Source: AgentOS/docs/audits/code-quality-audit.md*
*Project-specific quality requirements extend this framework.*
