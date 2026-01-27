# Test Workflow Brief

**Date:** 2026-01-27
**Purpose:** Test the issue creation workflow end-to-end.

## Problem

Need to verify that the workflow:
- Calls Claude without preamble
- Shows Gemini verdict in terminal
- Has progress indicators
- Timestamps all LLM calls

## Proposed Solution

This is a test issue to verify the workflow improvements:
1. No narration in drafts
2. Visible Gemini feedback
3. Progress tracking with timestamps
4. Node execution visibility

## Success Criteria

- Draft starts with `#` title, no preamble
- Gemini verdict prints to terminal
- Every LLM call shows timestamp and duration
- User never waits >5s without feedback
