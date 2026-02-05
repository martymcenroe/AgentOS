# 0829 - Lambda Failure Remediation Audit

**Status:** [Under Development]
**Created:** 2026-02-05
**Frequency:** On incident, weekly proactive scan

---

## Purpose

Proactively detect Lambda errors via CloudWatch and either auto-fix or draft issues for human review.

---

## Scope

This audit applies to projects with AWS Lambda:
- Lambda function errors
- Timeout issues
- Memory exhaustion
- Cold start problems
- Integration failures (DynamoDB, API Gateway, etc.)

**Primary consumer:** Aletheia (Lambda backend monitoring)

---

## Checklist (Draft)

### Error Detection
- [ ] Query CloudWatch Logs for ERROR/Exception patterns
- [ ] Check Lambda metrics for invocation errors
- [ ] Check for timeout violations
- [ ] Check for memory limit breaches
- [ ] Check for throttling events

### Error Classification
- [ ] Transient errors (retry-able)
- [ ] Configuration errors (fixable)
- [ ] Code bugs (need PR)
- [ ] External service failures (document)
- [ ] Capacity issues (scale up)

### Auto-Fix Candidates
- [ ] Timeout too low → increase timeout
- [ ] Memory too low → increase memory
- [ ] Missing environment variable → add to config
- [ ] Stale layer version → update layer

### Issue Draft Candidates
- [ ] Code exceptions → draft bug issue with stack trace
- [ ] Integration failures → draft investigation issue
- [ ] Unknown errors → draft triage issue

### Remediation Tracking
- [ ] Auto-fixes logged with before/after
- [ ] Issues created linked to CloudWatch logs
- [ ] Remediation verified (error stops recurring)

---

## Implementation Notes

**Not yet implemented.** This audit was identified during Issue #19 (audit reorganization) as a useful framework for AWS Lambda monitoring.

To implement:
1. Create CloudWatch Logs Insights queries
2. Add Lambda metrics analysis scripts
3. Create auto-fix scripts for common issues
4. Create issue draft templates

**AWS CLI patterns:**
```bash
# Query recent errors
MSYS_NO_PATHCONV=1 aws logs filter-log-events \
  --log-group-name /aws/lambda/FunctionName \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s000)

# Get Lambda metrics
MSYS_NO_PATHCONV=1 aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=FunctionName \
  --start-time $(date -d '1 day ago' --utc +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date --utc +%Y-%m-%dT%H:%M:%SZ) \
  --period 3600 \
  --statistics Sum
```

---

## Audit Record

| Date | Auditor | Findings | Issues |
|------|---------|----------|--------|
| - | - | Not yet executed | - |
