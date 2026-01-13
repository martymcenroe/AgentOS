#!/usr/bin/env python3
"""
AgentOS Documentation Reference Updater

Finds and updates references to old Aletheia 0xxx-numbered docs
with new AgentOS semantic paths.

Usage:
    python tools/update-doc-refs.py --project /path/to/project [--dry-run]
    python tools/update-doc-refs.py --project /c/Users/mcwiz/Projects/Aletheia --dry-run

Options:
    --dry-run    Show what would be changed without modifying files
    --verbose    Show all matches found
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Mapping from old Aletheia numbers to new AgentOS paths
# Format: "old_pattern" -> "new_path"
REFERENCE_MAP: Dict[str, str] = {
    # Standards (00xx)
    "0002-coding-standards": "AgentOS:standards/coding-standards",
    "0004-orchestration-protocol": "AgentOS:standards/orchestration-protocol",
    "0005-testing-strategy": "AgentOS:standards/testing-strategy",
    "0006-mermaid-diagrams": "AgentOS:standards/mermaid-diagrams",
    "0009-session-closeout": "AgentOS:standards/session-closeout-protocol",
    "0010-standard-labels": "AgentOS:standards/standard-labels",
    "0015-agent-prohibited": "AgentOS:standards/agent-prohibited-actions",

    # Templates (01xx)
    "0100-TEMPLATE-GUIDE": "AgentOS:templates/template-guide",
    "0100-template-guide": "AgentOS:templates/template-guide",
    "0101-TEMPLATE-issue": "AgentOS:templates/issue-template",
    "0102-TEMPLATE-feature-lld": "AgentOS:templates/feature-lld-template",
    "0103-TEMPLATE-implementation-report": "AgentOS:templates/implementation-report-template",
    "0104-TEMPLATE-adr": "AgentOS:templates/adr-template",
    "0105-TEMPLATE-implementation-plan": "AgentOS:templates/implementation-plan-template",
    "0108-lld-pre-implementation": "AgentOS:templates/lld-pre-impl-review",
    "0111-TEMPLATE-test-script": "AgentOS:templates/test-script-template",
    "0113-TEMPLATE-test-report": "AgentOS:templates/test-report-template",

    # ADRs (02xx) - Generic ones moved to AgentOS
    "0207-ADR-single-identity": "AgentOS:adrs/single-identity-orchestration",
    "0210-ADR-git-worktree": "AgentOS:adrs/git-worktree-isolation",
    "0213-ADR-adversarial-audit": "AgentOS:adrs/adversarial-audit-philosophy",
    "0214-ADR-claude-staging": "AgentOS:adrs/claude-staging-pattern",
    "0215-ADR-test-first": "AgentOS:adrs/test-first-philosophy",

    # Skills (06xx)
    "0600-skill-instructions-index": "AgentOS:skills/skill-instructions-index",
    "0601-skill-gemini-lld": "AgentOS:skills/gemini-lld-review",
    "0602-skill-gemini-dual": "AgentOS:skills/gemini-dual-review",

    # Audits (08xx) - Generic ones moved to AgentOS
    "0800-common-audits": "AgentOS:audits/audit-index",
    "0807-agentos-audit": "AgentOS:audits/agentos-audit",
    "0808-audit-permission-permissiveness": "AgentOS:audits/permission-permissiveness",
    "0809-audit-security": "AgentOS:audits/security-audit",
    "0810-audit-privacy": "AgentOS:audits/privacy-audit",
    "0811-audit-accessibility": "AgentOS:audits/accessibility-audit",
    "0813-audit-code-quality": "AgentOS:audits/code-quality-audit",
    "0814-audit-license": "AgentOS:audits/license-compliance",
    "0815-audit-claude": "AgentOS:audits/claude-capabilities",
    "0818-audit-ai-management": "AgentOS:audits/ai-management-system",
    "0819-audit-ai-supply": "AgentOS:audits/ai-supply-chain",
    "0820-audit-explainability": "AgentOS:audits/explainability",
    "0821-audit-agentic": "AgentOS:audits/agentic-ai-governance",
    "0822-audit-bias": "AgentOS:audits/bias-fairness",
    "0823-audit-ai-incident": "AgentOS:audits/ai-incident-post-mortem",
    "0824-audit-permission-friction": "AgentOS:audits/permission-friction",
    "0825-audit-ai-safety": "AgentOS:audits/ai-safety-audit",
    "0898-horizon-scanning": "AgentOS:audits/horizon-scanning-protocol",
    "0899-meta-audit": "AgentOS:audits/meta-audit",

    # Runbooks (09xx)
    "0900-runbook-index": "AgentOS:runbooks/runbook-index",
    "0901-nightly-agentos": "AgentOS:runbooks/nightly-agentos-audit",
}


def find_references(content: str) -> List[Tuple[str, str, int]]:
    """Find all references to old 0xxx patterns in content.

    Returns list of (old_pattern, suggested_new, line_number)
    """
    matches = []
    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        for old_pattern, new_path in REFERENCE_MAP.items():
            # Match various forms: [text](0xxx...), `0xxx...`, docs/0xxx...
            patterns = [
                rf'\[([^\]]*)\]\([^)]*{re.escape(old_pattern)}[^)]*\)',  # markdown link
                rf'`{re.escape(old_pattern)}[^`]*`',  # backtick reference
                rf'docs/{re.escape(old_pattern)}',  # path reference
                rf'{re.escape(old_pattern)}\.md',  # .md reference
            ]

            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    matches.append((old_pattern, new_path, line_num))
                    break  # Don't double-count same line

    return matches


def scan_project(project_path: Path, verbose: bool = False) -> Dict[Path, List[Tuple[str, str, int]]]:
    """Scan all markdown files in project for old references."""
    results = {}

    for md_file in project_path.rglob("*.md"):
        # Skip certain directories
        if any(skip in str(md_file) for skip in ['.git', 'node_modules', 'legacy']):
            continue

        try:
            content = md_file.read_text(encoding='utf-8')
            matches = find_references(content)

            if matches:
                results[md_file] = matches
                if verbose:
                    print(f"\n{md_file.relative_to(project_path)}:")
                    for old, new, line in matches:
                        print(f"  Line {line}: {old} -> {new}")
        except Exception as e:
            print(f"Warning: Could not read {md_file}: {e}")

    return results


def generate_report(results: Dict[Path, List[Tuple[str, str, int]]], project_path: Path) -> str:
    """Generate a markdown report of findings."""
    lines = [
        "# Cross-Reference Update Report",
        "",
        f"**Project:** {project_path}",
        f"**Files with references:** {len(results)}",
        f"**Total references:** {sum(len(v) for v in results.values())}",
        "",
        "## Files Requiring Updates",
        "",
    ]

    for file_path, matches in sorted(results.items()):
        rel_path = file_path.relative_to(project_path)
        lines.append(f"### {rel_path}")
        lines.append("")
        lines.append("| Line | Old Reference | New Reference |")
        lines.append("|------|---------------|---------------|")
        for old, new, line_num in matches:
            lines.append(f"| {line_num} | `{old}` | `{new}` |")
        lines.append("")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description="Update documentation cross-references")
    parser.add_argument("--project", required=True, help="Path to project to scan")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without modifying")
    parser.add_argument("--verbose", action="store_true", help="Show all matches")
    parser.add_argument("--report", help="Write report to file")

    args = parser.parse_args()

    project_path = Path(args.project).resolve()
    if not project_path.exists():
        print(f"Error: Project path does not exist: {project_path}")
        return 1

    print(f"Scanning {project_path} for old references...")
    results = scan_project(project_path, verbose=args.verbose)

    if not results:
        print("\nNo old references found!")
        return 0

    print(f"\nFound {sum(len(v) for v in results.values())} references in {len(results)} files")

    # Generate report
    report = generate_report(results, project_path)

    if args.report:
        Path(args.report).write_text(report)
        print(f"\nReport written to: {args.report}")
    else:
        print("\n" + "="*60)
        print(report)

    if args.dry_run:
        print("\n[DRY RUN] No files were modified.")
    else:
        print("\nTo update files, review the report and make changes manually.")
        print("Automated replacement coming in future version.")

    return 0


if __name__ == "__main__":
    exit(main())
