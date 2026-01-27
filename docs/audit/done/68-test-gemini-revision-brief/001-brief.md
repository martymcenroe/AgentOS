# Incomplete Brief to Test Gemini Revision Flow

**Date:** 2026-01-27
**Purpose:** Create a brief that's intentionally missing required sections so Gemini flags it, forcing a revision.

## Problem

This brief is missing:
- User Story (required by template)
- Security Considerations (required by template)
- Files to Create/Modify section
- Acceptance Criteria details

## Proposed Solution

Just add a new button somewhere. That's it. No details.

## Expected Gemini Feedback

Gemini should flag:
- Missing User Story
- Missing Security Considerations
- Vague implementation details
- Missing file paths
- Incomplete acceptance criteria

## Test Verification

After Claude revises based on Gemini's feedback, the draft should include:
- A proper "As a user..." User Story
- Security Considerations section
- Files to Create/Modify with actual paths
- Detailed Acceptance Criteria
