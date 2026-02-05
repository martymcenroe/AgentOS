# 0827 - Infrastructure Integration Audit

**Status:** [Under Development]
**Created:** 2026-02-05
**Frequency:** Monthly, on infrastructure changes

---

## Purpose

Verify AWS infrastructure components (Lambda, DynamoDB, API Gateway) are correctly configured and integrated.

---

## Scope

This audit applies to projects with AWS infrastructure:
- Lambda functions
- DynamoDB tables
- API Gateway endpoints
- IAM roles and policies
- CloudWatch alarms

**Primary consumer:** Aletheia (Lambda backend for extension)

---

## Checklist (Draft)

### Lambda Functions
- [ ] All functions deploy successfully
- [ ] Memory/timeout settings appropriate
- [ ] Environment variables set correctly
- [ ] VPC configuration correct (if applicable)
- [ ] Layers attached and versions current

### DynamoDB Tables
- [ ] Tables exist with correct schema
- [ ] GSIs/LSIs configured correctly
- [ ] Capacity mode appropriate (on-demand vs provisioned)
- [ ] TTL configured if needed
- [ ] Backup/PITR enabled if required

### API Gateway
- [ ] Endpoints respond correctly
- [ ] Auth configured (API keys, Cognito, IAM)
- [ ] CORS settings correct
- [ ] Throttling/quota limits appropriate
- [ ] Custom domain configured (if applicable)

### IAM
- [ ] Lambda execution roles have minimum necessary permissions
- [ ] No overly permissive policies (*, Resource: *)
- [ ] Cross-account access documented if present

### Monitoring
- [ ] CloudWatch alarms configured for errors
- [ ] Log retention policies set
- [ ] X-Ray tracing enabled (if needed)

---

## Implementation Notes

**Not yet implemented.** This audit was identified during Issue #19 (audit reorganization) as a useful framework for AWS-based projects.

To implement:
1. Create AWS CLI verification scripts
2. Add Terraform/CloudFormation drift detection
3. Create IAM policy analyzer

---

## Audit Record

| Date | Auditor | Findings | Issues |
|------|---------|----------|--------|
| - | - | Not yet executed | - |
