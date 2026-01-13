# 0820 - Audit: Explainability (XAI)

## 1. Purpose

Ensure AI systems provide understandable, traceable explanations for their outputs. Covers Explainable AI (XAI) requirements for transparency, regulatory compliance, and user trust.

**Aletheia Context:**
- Etymology analysis outputs must be understandable
- Guardrail decisions (block/allow) should be traceable
- EU AI Act Article 13 requires transparency for certain AI systems
- User trust depends on understanding why AI produced specific output

---

## 2. Explainability Requirements

### 2.1 Regulatory Requirements

| Regulation | Requirement | Aletheia Applicability | Status |
|------------|-------------|------------------------|--------|
| **EU AI Act Art. 13** | High-risk systems must be interpretable | Low risk (informational) | N/A |
| **EU AI Act Art. 52** | Users must know they're interacting with AI | All AI systems | |
| **GDPR Art. 22** | Right to explanation for automated decisions | No automated decisions | N/A |
| **CCPA** | Disclosure of AI use | California users | |

### 2.2 User Trust Requirements

| Requirement | Why It Matters | Status |
|-------------|----------------|--------|
| Clear AI disclosure | Users know it's AI | |
| Output reasoning visible | Users understand analysis | |
| Confidence indication | Uncertainty communicated | |
| Limitation disclosure | Users know boundaries | |

---

## 3. Etymology Output Explainability

### 3.1 Output Structure Analysis

The etymologist persona should provide explanations, not just conclusions.

| Check | Requirement | Verification | Status |
|-------|-------------|--------------|--------|
| Historical context | Origin story provided | Review sample outputs | |
| Language evolution | How meaning changed | Review sample outputs | |
| Cultural context | Social/historical factors | Review sample outputs | |
| Uncertainty markers | "possibly," "likely," "uncertain" | Grep prompt/outputs | |
| Source attribution | Where information comes from | Review prompt design | |

### 3.2 Explanation Quality Checklist

```bash
# Check etymologist prompt for explanation requirements
🤖 grep -A 20 "system_prompt" src/guardrails/etymologist.py
```

| Quality Dimension | Check | Status |
|-------------------|-------|--------|
| **Completeness** | Does output address the query fully? | |
| **Accuracy** | Is the etymology factually correct? | |
| **Clarity** | Is language accessible to non-experts? | |
| **Neutrality** | Is tone balanced and educational? | |
| **Attribution** | Are sources or reasoning visible? | |

### 3.3 Sample Output Review

Test with diverse inputs and evaluate explanations:

| Input Type | Sample | Expected Explanation Quality |
|------------|--------|------------------------------|
| Common word | "hello" | Clear origin, usage evolution |
| Slur (blocked) | [blocked term] | Graceful rejection, no analysis |
| Technical term | "algorithm" | Etymology with historical context |
| Borrowed word | "karaoke" | Cross-language origin explained |
| Ambiguous word | "nice" | Multiple historical meanings shown |

---

## 4. Guardrail Decision Explainability

### 4.1 Selection Check (Input Validation)

| Decision Point | Is Reasoning Logged? | Can User Understand? | Status |
|----------------|----------------------|----------------------|--------|
| Too short | Yes (< 2 chars) | Yes - clear threshold | |
| Too long | Yes (> 20k chars) | Yes - clear threshold | |
| Empty input | Yes | Yes - obvious | |

### 4.2 Denylist Filter

| Decision Point | Is Reasoning Logged? | Can User Understand? | Status |
|----------------|----------------------|----------------------|--------|
| Term blocked | Logged internally | No - generic message | |
| Term allowed | Not logged | N/A | |

**Improvement Opportunity:** Should blocked terms provide user feedback? Currently: generic error. Consider: "This term was not analyzed due to content policy."

### 4.3 Semantic Guardrail

| Decision Point | Is Reasoning Logged? | Can User Understand? | Status |
|----------------|----------------------|----------------------|--------|
| Content classified | CloudWatch (category) | No - internal only | |
| Blocked category | Generic error | Minimal explanation | |

```bash
# Check what information is logged for guardrail decisions
🤖 grep -n "logger\|logging\|print" src/guardrails/*.py
```

### 4.4 Guardrail Transparency Assessment

| Layer | Decision Transparency | User Feedback | Internal Logging | Status |
|-------|----------------------|---------------|------------------|--------|
| Selection | High | Clear | Yes | ✅ |
| Denylist | Low | Generic | Yes | ⚠️ |
| Semantic | Low | Generic | Partial | ⚠️ |
| Transform | High | Output visible | N/A | ✅ |

---

## 5. Audit Trail Completeness

### 5.1 Request Tracing

| Event | Logged? | Traceable? | Status |
|-------|---------|------------|--------|
| Request received | Yes (thread_id) | Yes | |
| Selection check result | No | No | |
| Denylist check result | No | No | |
| Semantic check result | Partial | Partial | |
| Bedrock call | Yes (CloudWatch) | Yes | |
| Response sent | Yes (thread_id) | Yes | |

### 5.2 Debug Explainability

Can a developer understand why a specific request was handled a certain way?

```bash
# Given a thread_id, can we trace the full decision path?
# 1. Find in CloudWatch
# 2. Identify which guardrail triggered (if any)
# 3. See the LLM response

# Current state: Partial - guardrail decisions not fully logged
```

### 5.3 Recommended Improvements

| Improvement | Priority | Effort |
|-------------|----------|--------|
| Log guardrail pass/fail per layer | Medium | Low |
| Add decision reason to DynamoDB | Low | Medium |
| User-facing guardrail feedback | Low | Medium |
| Structured logging format | Medium | Medium |

---

## 6. XAI Techniques Assessment

### 6.1 Applicable XAI Methods

| Technique | Applicability | Implementation | Status |
|-----------|---------------|----------------|--------|
| **Feature Attribution** | Low (no custom model) | N/A | N/A |
| **SHAP/LIME** | Low (API-based) | N/A | N/A |
| **Attention Visualization** | Low (no access) | N/A | N/A |
| **Chain-of-Thought** | High | Prompt engineering | |
| **Self-Explanation** | High | Prompt requests reasoning | |
| **Confidence Scoring** | Medium | Could add to prompt | |

### 6.2 Prompt-Based Explainability

Since Aletheia uses API-based models, explainability comes through prompt engineering:

```bash
# Check if prompt requests explanation/reasoning
🤖 grep -i "explain\|reason\|why\|because" src/guardrails/etymologist.py
```

| Prompt Feature | Present? | Status |
|----------------|----------|--------|
| Requests explanation | | |
| Encourages reasoning | | |
| Asks for uncertainty markers | | |
| Requires source citation | | |

---

## 7. User Communication

### 7.1 AI Disclosure

| Location | AI Disclosed? | How? | Status |
|----------|---------------|------|--------|
| Store listing | | "AI-powered" | |
| Extension popup | | AI mention | |
| Context menu | | "Explain with AI" | |
| Output overlay | | Attribution | |
| README | | Feature description | |
| Wiki | | Technical details | |

### 7.2 Limitation Disclosure

| Limitation | Disclosed? | Where? | Status |
|------------|------------|--------|--------|
| AI can be wrong | | Store listing/README | |
| Not a dictionary | | Documentation | |
| Internet required | | Store listing | |
| English focused | | Documentation | |
| Some content blocked | | Privacy docs | |

---

## 8. Audit Procedure

1. **Review Prompt Engineering**
   - Check etymologist prompt for explanation requirements
   - Verify neutral, educational tone instructions
   - Look for uncertainty/confidence handling

2. **Test Output Explainability**
   - Run 5-10 diverse test cases
   - Evaluate explanation quality per §3.3
   - Document any unexplained outputs

3. **Audit Decision Logging**
   - Trace a request through full pipeline
   - Verify guardrail decisions are traceable
   - Identify logging gaps

4. **Verify User Communication**
   - Check all user-facing surfaces for AI disclosure
   - Verify limitation disclosures are present
   - Update documentation if needed

---

## 9. Audit Record

| Date | Auditor | Findings Summary | Issues Created |
|------|---------|------------------|----------------|
| 2026-01-10 | Claude Opus 4.5 | PASS: AI disclosure present in popup.html ("AI-powered context analysis"), etymologist persona provides structured explanations (signal, gem, context format), uncertainty markers in prompt design, clear classification rules | None |

---

## 10. References

### Frameworks
- [EU AI Act Article 13](https://artificialintelligenceact.eu/article/13/) - Transparency
- [NIST AI RMF - MEASURE](https://www.nist.gov/itl/ai-risk-management-framework) - Explainability
- [ISO/IEC 42001 Annex A](https://www.iso.org/standard/42001) - Transparency controls

### XAI Techniques
- [SHAP (SHapley Additive exPlanations)](https://shap.readthedocs.io/)
- [LIME (Local Interpretable Model-agnostic Explanations)](https://github.com/marcotcr/lime)

### Internal
- docs/0809-audit-security.md §3 - LLM security (prompt injection defense)
- src/guardrails/etymologist.py - Prompt engineering

---

## 11. History

| Date | Change |
|------|--------|
| 2026-01-06 | Created. XAI audit for etymology output and guardrail decision transparency. |
