# {{PROJECT_NAME}} - Quality Attributes

Non-functional requirements and their current status for {{PROJECT_NAME}}.

## Performance

| Metric | Target | Current | Evidence |
|--------|--------|---------|----------|
| Response Latency | <500ms | TBD | [Performance Audit](audits/performance.md) |
| Throughput | >100 rps | TBD | Load test results |
| Memory Usage | <512MB | TBD | Monitoring |

## Reliability

| Metric | Target | Current | Evidence |
|--------|--------|---------|----------|
| Uptime | 99.9% | TBD | Monitoring dashboard |
| Error Rate | <0.1% | TBD | Error tracking |
| Recovery Time | <5min | TBD | Incident logs |

## Security

| Requirement | Target | Current | Evidence |
|-------------|--------|---------|----------|
| Authentication | Required | TBD | [Security Audit](audits/security.md) |
| Authorization | RBAC | TBD | Code review |
| Data Encryption | At rest + transit | TBD | Infrastructure config |

## Privacy

| Requirement | Target | Current | Evidence |
|-------------|--------|---------|----------|
| PII Handling | Minimized | TBD | [Privacy Audit](audits/privacy.md) |
| Data Retention | Policy-based | TBD | Data lifecycle docs |
| User Consent | Explicit | TBD | UI review |

## Accessibility

| Requirement | Target | Current | Evidence |
|-------------|--------|---------|----------|
| WCAG Level | 2.1 AA | TBD | [Accessibility Audit](audits/accessibility.md) |
| Keyboard Navigation | Full | TBD | Manual testing |
| Screen Reader | Compatible | TBD | Assistive tech testing |

## Maintainability

| Metric | Target | Current | Evidence |
|--------|--------|---------|----------|
| Code Coverage | >80% | TBD | CI reports |
| Documentation | Complete | TBD | Doc audit |
| Complexity | Low | TBD | Static analysis |

---

[← ADR Digest](0001d-adr-digest.md) | [Deployment View →](0001f-deployment-view.md)
