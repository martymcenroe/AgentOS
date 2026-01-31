# 93 - Feature: The Scout: External Intelligence Gathering Workflow

## 1. Context & Goal
* **Issue:** #93
* **Objective:** Create a proactive research workflow that searches GitHub/Web for solutions to a given problem, analyzes top implementations using Gemini 1.5 Flash, compares them against internal code, and produces an "Innovation Brief" documenting deficiencies.
* **Status:** Draft
* **Related Issues:** None - requirements are well-defined from issue.

### Open Questions
None - requirements are well-defined from issue.

## 2. Proposed Changes

### 2.1 Files Changed
| File Path | Description |
|-----------|-------------|
| `agentos/workflows/scout/__init__.py` | Package initialization. |
| `agentos/workflows/scout/constants.py` | Configuration constants (LLM_MODEL="gemini-1.5-flash", MAX_REPOS=3, TOKEN_LIMITS). |
| `agentos/workflows/scout/graph.py` | LangGraph state machine definition (Explorer → Extractor → Gap Analyst → Scribe). |
| `agentos/workflows/scout/nodes.py` | Node implementations (Explorer, Extractor, Gap Analyst, Scribe). |
| `agentos/workflows/scout/prompts.py` | LLM prompts for gap analysis and summarization. |
| `agentos/workflows/scout/templates.py` | Jinja2 templates for Innovation Brief Markdown generation. |
| `agentos/workflows/scout/token_estimator.py` | Token counting and budget enforcement logic. |
| `tools/run_scout_workflow.py` | CLI entry point handling args, privacy warnings, path safety, and output generation. |
| `tests/workflows/scout/test_graph.py` | Integration tests for graph state transitions. |
| `tests/workflows/scout/test_nodes.py` | Unit tests for individual nodes with mocked APIs. |
| `tests/workflows/scout/test_token_estimator.py` | Unit tests for token budget enforcement. |
| `tests/fixtures/golden-brief-summary.md` | Golden fixture for similarity testing. |
| `ideas/active/.gitkeep` | Ensure output directory exists. |
| `agentos/workflows/__init__.py` | Register scout workflow. |
| `docs/0003-file-inventory.md` | Update inventory. |

### 2.2 Dependencies
| Dependency | Purpose |
|------------|---------|
| `PyGithub` | Interaction with GitHub API for search, content retrieval, and license metadata. |
| `tiktoken` | Local token estimation to enforce budgets before LLM calls. |
| `rich` | CLI UI formatting, progress spinners, and interactive prompts. |
| `tenacity` | Exponential backoff for API rate limit handling. |
| `jinja2` | Templating engine for generating consistent Markdown briefs. |

### 2.3 Data Structures

```python
from typing import TypedDict, List, Optional, Any

class RepositoryData(TypedDict):
    name: str           # "owner/repo"
    url: str            # HTML URL
    stars: int
    description: str
    license_type: str   # SPDX ID (e.g., "MIT") or "Unknown"
    readme_content: str # Truncated content
    arch_content: str   # Truncated content of architecture/design docs if found

class ScoutState(TypedDict):
    # Input
    topic: str
    internal_file_path: Optional[str]
    internal_file_content: Optional[str]
    min_stars: int
    max_tokens: int
    max_repos: int      # Hard limit on external sources to analyze
    
    # Intermediate
    found_repos: List[RepositoryData]    # Metadata from search
    analyzed_repos: List[RepositoryData] # Populated with content
    gap_analysis_result: str             # LLM output
    
    # Output
    brief_content: str
    output_path: str
    error: Optional[str]
```

### 2.4 Function Signatures

**`agentos/workflows/scout/constants.py`**
```python
MAX_REPOS_TO_ANALYZE = 3
MAX_CHARS_PER_FILE = 15000
DEFAULT_TOKEN_BUDGET = 30000
LLM_MODEL_TIER = "gemini-1.5-flash"
OUTPUT_DIR = "ideas/active"
```

**`tools/run_scout_workflow.py`**
```python
def confirm_transmission(file_path: str, force_yes: bool) -> bool:
    """
    Displays a warning using 'rich' about data transmission to Gemini.
    Returns True if user confirms (y) or force_yes is True.
    """
    pass

def validate_safe_input_path(path: str) -> str:
    """
    Ensures path is within project root to prevent traversal.
    Checks file existence.
    Raises ValueError if invalid.
    """
    pass

def resolve_output_path(topic: str, custom_path: Optional[str]) -> str:
    """
    Sanitizes topic to create filename (e.g., 'innovation-langgraph-patterns.md').
    Ensures output directory exists.
    Raises FileExistsError if the target file already exists (no silent overwrite).
    """
    pass

def main():
    """CLI Entry point: Parses args, runs pre-flight checks, invokes graph."""
    pass
```

**`agentos/workflows/scout/token_estimator.py`**
```python
def estimate_tokens(text: str) -> int:
    """Returns token count using cl100k_base encoding."""
    pass

def check_budget_preflight(internal_content: Optional[str], limit: int) -> None:
    """
    Estimates total tokens including reserved buffer for external content (approx 15k tokens).
    Raises BudgetExceededError if limit is breached.
    """
    pass
```

**`agentos/workflows/scout/nodes.py`**
```python
def node_explorer(state: ScoutState) -> dict:
    """
    Searches GitHub for repos > min_stars matching topic.
    Slices results to state['max_repos'].
    Returns: {'found_repos': [metadata_list]}
    """
    pass

def node_extractor(state: ScoutState) -> dict:
    """
    Fetches README/License for found repos via PyGithub.
    Applies strict truncation limits (MAX_CHARS_PER_FILE).
    Captures license.spdx_id.
    Returns: {'analyzed_repos': [full_data_list]}
    """
    pass

def node_gap_analyst(state: ScoutState) -> dict:
    """
    Invokes Gemini 1.5 Flash to compare internal vs external patterns.
    Returns: {'gap_analysis_result': str}
    """
    pass

def node_scribe(state: ScoutState) -> dict:
    """
    Formats final report using Jinja2 templates.
    Returns: {'brief_content': str}
    """
    pass
```

### 2.5 Logic Flow (Pseudocode)

**CLI Main Workflow**
```python
def main():
    args = parse_args() # topic, internal, min_stars, max_tokens, output, dry_run, yes, format
    
    # 1. Input Validation & Safety
    internal_content = None
    if args.internal:
        path = validate_safe_input_path(args.internal)
        with open(path, 'r', encoding='utf-8') as f:
            internal_content = f.read()

    # 2. Privacy Gate
    if internal_content and not confirm_transmission(args.internal, args.yes):
        print("Aborted by user.")
        sys.exit(0)

    # 3. Cost Control Pre-flight
    try:
        # Check if internal file + estimated external content fits in budget
        # Buffer for external content is approx 15k tokens (3 repos * 5k tokens each)
        check_budget_preflight(internal_content, args.max_tokens)
    except BudgetExceededError as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    # 4. Output Path Resolution
    try:
        output_path = resolve_output_path(args.topic, args.output)
    except FileExistsError:
        print(f"Error: Output file already exists. Please move it or specify --output.")
        sys.exit(1)

    # 5. Graph Execution
    state = {
        "topic": args.topic,
        "internal_file_content": internal_content,
        "internal_file_path": args.internal,
        "min_stars": args.min_stars,
        "max_tokens": args.max_tokens,
        "max_repos": 3 # Hard limit
    }
    
    if args.dry_run:
        print_plan(state, output_path)
        return

    app = WorkflowGraph.compile()
    result = app.invoke(state)
    
    # 6. Final Output
    if args.format == 'json':
        print(json.dumps(result, indent=2))
    else:
        with open(output_path, 'w') as f:
            f.write(result["brief_content"])
        print(f"Brief saved to {output_path}")
```

**Extractor Node (License & Bounds)**
```python
def node_extractor(state: ScoutState):
    github = get_github_client()
    analyzed = []
    
    for repo_meta in state['found_repos']:
        repo = github.get_repo(repo_meta['name'])
        
        # License Extraction
        try:
            license_obj = repo.get_license()
            license_id = license_obj.license.spdx_id if license_obj else "None"
        except Exception:
            license_id = "Unknown"
            
        # Content Fetching with Truncation
        readme = fetch_readme(repo) # Handles exceptions
        truncated_readme = readme[:MAX_CHARS_PER_FILE]
        
        analyzed.append({
            **repo_meta,
            "license_type": license_id,
            "readme_content": truncated_readme,
            "arch_content": "" # Optional fetch if architecture.md exists
        })
        
    return {"analyzed_repos": analyzed}
```

### 2.6 Technical Approach
*   **Module Location:** `agentos/workflows/scout/`
*   **Design Pattern:** State Machine (LangGraph).
*   **LLM Model:** **Gemini 1.5 Flash** (hardcoded to balance cost/performance).
*   **Safety Handling:**
    *   **Input:** Path traversal validation prevents reading sensitive system files.
    *   **Output:** Explicit check for existing files to prevent accidental overwrite (Reviewer feedback addressed).
    *   **Privacy:** Explicit CLI gate prevents accidental data leakage.
*   **Cost Management:** A "Pre-flight" check uses `tiktoken` to estimate costs *before* any API calls are made.

## 3. Requirements
1.  **Search:** Interface with GitHub API to find repositories > star threshold (default 500).
2.  **Repo Limit:** Analyze max 3 top repositories per run.
3.  **License Identification:** Explicitly capture `license.spdx_id` (e.g., MIT, Apache-2.0) for every external source.
4.  **Privacy Protection:** Require confirmation before transmitting internal code to Gemini.
5.  **Budget Enforcement:** Abort if estimated tokens > limit (default 30k).
6.  **Defensive Processing:** Truncate external inputs (15k chars) to prevent context overflow.
7.  **Output Safety:** Prevent path traversal in output file generation and error on file existence (no overwrite).
8.  **Output Formatting:** Generate Markdown (default) or JSON.

## 4. Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| **Web Scraping (BeautifulSoup)** | No API limits. | Fragile, maintenance heavy. | **Rejected** - Use GitHub API. |
| **Git Clone Analysis** | Full codebase access. | Slow, disk heavy, security risks. | **Rejected** - Analyze README/Docs via API only. |
| **Gemini 1.5 Pro** | Higher reasoning capability. | Significantly higher cost ($5-10/run). | **Rejected** - Use Flash (~$0.10/run). |
| **Auto-Overwrite Output** | Convenience. | Risk of data loss. | **Rejected** - Fail if file exists. |

## 5. Data & Fixtures

### 5.1 Data Sources
| Source | Attributes |
|--------|------------|
| **GitHub Search API** | `full_name`, `stargazers_count`, `html_url` |
| **GitHub Contents API** | `content` (base64), `encoding` |
| **GitHub License API** | `license.spdx_id` |
| **Local File System** | Source code text (UTF-8) |

### 5.2 Data Pipeline
```ascii
[CLI] -> [Input Validation] -> [Budget Check] -> [Privacy Check]
                                     |
                                     v
                            [LangGraph Execution]
                                     |
[GitHub API] <--(Search/Fetch)-- [Nodes] --(Analysis)--> [Gemini 1.5 Flash]
                                     |
                                     v
                            [Output Generation] -> [File System]
```

### 5.3 Test Fixtures
| Fixture | Description |
|---------|-------------|
| `golden-brief-summary.md` | Expected Markdown output for similarity testing. |
| `mock_gh_search.json` | Sample GitHub Search API response. |
| `mock_gh_license.json` | Sample GitHub License API response. |

### 5.4 Deployment Pipeline
*   **Development only:** Runs locally via CLI.
*   **Env Vars:** `GITHUB_TOKEN`, `GEMINI_API_KEY`.

## 6. Diagram

### 6.1 Mermaid Quality Gate
- [x] Diagram type: Sequence
- [x] Participants defined
- [x] Flows clearly shown

### 6.2 Diagram
```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Graph
    participant GitHub
    participant GeminiFlash

    User->>CLI: run --topic "X" --internal "Y"
    CLI->>CLI: Validate Paths & Estimate Tokens
    alt Over Budget
        CLI-->>User: Error: Budget Exceeded
    end
    CLI->>User: Warning: Send "Y" to Cloud?
    User-->>CLI: Yes
    
    CLI->>Graph: Invoke(State)
    Graph->>GitHub: Search(topic, stars>500)
    GitHub-->>Graph: [Repo A, Repo B, Repo C]
    
    loop For Top 3 Repos
        Graph->>GitHub: Get License ID
        Graph->>GitHub: Get README
        Graph->>Graph: Truncate Content (15k chars)
    end
    
    Graph->>GeminiFlash: Prompt(Internal + External)
    GeminiFlash-->>Graph: Gap Analysis
    
    Graph->>Graph: Scribe (Format Markdown)
    Graph-->>CLI: Final Brief
    
    alt File Exists
        CLI-->>User: Error: File exists
    else
        CLI->>CLI: Write File
        CLI->>User: Saved to ideas/active/innovation-X.md
    end
```

## 7. Security Considerations

| Concern | Mitigation |
|---------|------------|
| **Internal Code Leakage** | Code sent ONLY to Gemini (HTTPS). User must confirm via interactive prompt or `--yes`. |
| **Path Traversal (Input)** | CLI validates `--internal` path is within project root. |
| **Path Traversal (Output)** | Output filename sanitization; writing restricted to `ideas/active/` or user provided path. |
| **Overwrite Risks** | CLI raises error if output file exists. |
| **GitHub Rate Limits** | `tenacity` retry logic with exponential backoff. |

## 8. Performance Considerations

| Metric | Budget |
|--------|--------|
| **Search Latency** | < 2 seconds |
| **Total Runtime** | < 45 seconds (typical) |
| **Token Usage** | Max 30,000 tokens per run (hard cap) |
| **Model** | Gemini 1.5 Flash (Fixed tier) |

## 9. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **API Rate Limit (GitHub)** | Workflow fails | Medium | Backoff logic + User instruction to provide token. |
| **LLM Cost Spike** | Unexpected bill | Low | Strict pre-flight token estimation and hard cap. |
| **Context Overflow** | Error | Medium | Strict 15k char truncation per file. |

## 10. Verification & Testing

### 10.1 Test Scenarios
| ID | Scenario | Type | Input | Output | Criteria |
|----|----------|------|-------|--------|----------|
| 1 | Happy Path | E2E | Topic="State", Internal="file.py", Yes=True | .md File | Contains license info & gaps. |
| 2 | Budget Exceeded | Unit | `--max-tokens 100` | Error | Exits before API call. |
| 3 | Privacy Decline | E2E | `--internal file.py` (User inputs 'n') | Message | "Aborted". |
| 4 | Output Exists | E2E | Topic="Existing" | Error | "File exists" error. |
| 5 | JSON Format | E2E | `--format json` | stdout | Valid JSON. |

### 10.2 Test Commands
```bash
# Unit tests
pytest tests/workflows/scout/

# Brief similarity check
pytest tests/workflows/scout/test_brief_similarity.py

# Manual dry run (Checks cost estimation)
python tools/run_scout_workflow.py --topic "agents" --dry-run
```

### 10.3 Manual Tests (Only If Unavoidable)
N/A - All scenarios automated.

## 11. Definition of Done

### Code
- [ ] `run_scout_workflow.py` implemented with path safety and privacy gates.
- [ ] `token_estimator.py` implements tiktoken logic and pre-flight check.
- [ ] Graph nodes implemented with defensive truncation and license extraction.
- [ ] `GEMINI_MODEL_TIER` configured to `gemini-1.5-flash`.
- [ ] Overwrite protection implemented.

### Tests
- [ ] >80% coverage on new module.
- [ ] Integration tests verify graph lifecycle.
- [ ] Golden fixture test passes.

### Documentation
- [ ] CLI tool help text is complete.
- [ ] Privacy implications documented.

### Review
- [ ] Security review of path validation logic.
- [ ] UX review of CLI prompts.

---

## Appendix: Review Log

### Review Summary

| Review | Date | Verdict | Key Issue |
|--------|------|---------|-----------|
| - | - | - | - |

**Final Status:** DRAFT - PENDING REVIEW