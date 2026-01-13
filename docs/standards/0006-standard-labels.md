# 0010 - Standard Labels & Taxonomy

## Purpose

To ensure consistent categorization of work across the Aletheia project. All issues and PRs must have at least one `Type` label.

## Label Taxonomy

### 1. Types (Mutually Exclusive)

| Label | Color | Description |
| --- | --- | --- |
| `feature` | Blue | New functionality for the user. |
| `bug` | Red | Something is broken. |
| `chore` | Grey | Maintenance, docs, tooling (no user-facing change). |
| `security` | Green | Vulnerability fixes or hardening. |

### 2. Priority

| Label | Color | Description |
| --- | --- | --- |
| `high-priority` | Dark Red | Blocks release or critical path. |
| `low-priority` | Yellow | Nice to have, can wait. |

### 3. Status (Automated via KanBan, but good to know)

| Label | Description |
| --- | --- |
| `wontfix` | Abandoned or out of scope. |
| `duplicate` | Merged into another issue. |

## Usage with GitHub CLI

When creating an issue, use the exact slug (case-sensitive):

```bash
gh issue create --label "chore,high-priority"

```
