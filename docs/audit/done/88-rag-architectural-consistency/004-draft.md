# RAG Injection: Automated Context Retrieval ("The Librarian")

## User Story
As an **LLD Designer Agent**,
I want **relevant ADRs and standards automatically retrieved and injected into my context**,
So that **I don't propose solutions that violate established architectural decisions**.

## Objective
Implement an automated RAG (Retrieval-Augmented Generation) node that queries a local vector store with the issue brief and injects the top-3 most relevant governance documents into the Designer's context.

## UX Flow

### Scenario 1: Happy Path - Relevant Documents Found
1. User runs `agentos lld create --brief "Implement distributed error logging"`
2. Librarian Node embeds the brief and queries the vector store
3. System retrieves `docs/LLDs/done/57-distributed-logging.md` (score: 0.89), `docs/standards/0002-coding-standards.md` (score: 0.82), `docs/adrs/0204-single-identity-orchestration.md` (score: 0.71)
4. Retrieved documents are silently appended to Designer context
5. Designer references these constraints in the generated LLD without user prompting
6. Result: LLD aligns with existing architecture

### Scenario 2: No Relevant Documents Found
1. User runs `agentos lld create --brief "Add support for Klingon language localization"`
2. Librarian Node queries the vector store
3. All results score below 0.7 threshold
4. System logs: `[Librarian] No relevant governance documents found (best score: 0.42)`
5. Workflow continues with only manual `--context` if provided
6. Result: Designer proceeds without RAG augmentation

### Scenario 3: Manual Context Override
1. User runs `agentos lld create --brief "..." --context docs/adrs/0199-special-case.md`
2. Librarian retrieves 3 documents automatically
3. System merges: manual context takes precedence, duplicates removed
4. Result: Final context = manual selections + RAG selections (deduplicated)

### Scenario 4: Vector Store Not Initialized
1. User runs `agentos lld create --brief "..."`
2. Librarian checks for `.agentos/vector_store/` — not found
3. System logs warning: `[Librarian] Vector store not found. Run 'tools/rebuild_knowledge_base.py' to enable RAG.`
4. Workflow continues without RAG augmentation
5. Result: Graceful degradation to manual-only context

### Scenario 5: Cold Boot with CLI Spinner
1. User runs `agentos lld create --brief "..."` for the first time in a session
2. Vector store/embedding model loading begins
3. CLI displays spinner: `[Librarian] Loading embedding model...`
4. If loading exceeds 500ms, spinner remains visible until complete
5. Result: User has feedback during potentially slow cold-boot operations

## Requirements

### Vector Infrastructure
1. Use ChromaDB for local, file-based vector storage (no external dependencies for default mode)
2. Store vector database in `.agentos/vector_store/`
3. Support embedding models: `all-MiniLM-L6-v2` (default/local) or OpenAI/Gemini if API key available
4. Index all markdown files in `docs/adrs/`, `docs/standards/`, and `docs/LLDs/done/`
5. Split documents by H1/H2 headers for granular retrieval

### Librarian Node
1. Accept `issue_brief` text as input
2. Query vector store for k=5 candidates, return top 3 after filtering
3. Apply similarity score threshold of 0.7 (configurable)
4. Return list of `{file_path, section, content_snippet, score}`
5. Complete retrieval in < 500ms for typical queries (after model warm-up)
6. Display CLI spinner during model/vector store loading on cold boot

### Workflow Integration
1. Insert Librarian Node between "Load Brief" and "Designer" nodes
2. Merge RAG results with manual `--context` (manual wins on conflicts)
3. Pass combined context to Designer node
4. Log retrieved documents at INFO level for transparency

### Ingestion Tool
1. Provide `tools/rebuild_knowledge_base.py` for manual reindexing
2. Support incremental updates (only reindex changed files)
3. Complete full reindex of ~100 files in < 10 seconds
4. Output summary: files indexed, chunks created, time elapsed

### Technical Verification
1. Verify `pyproject.toml` updates do not break existing lightweight installations
2. Test dependency compatibility on standard CI environments (Linux/Mac/Windows)
3. Document known `chromadb` compatibility issues with `sqlite` versions and `pydantic` conflicts
4. Provide fallback instructions if dependency conflicts occur

## Technical Approach
- **ChromaDB:** Persistent local vector store with HNSW index for fast similarity search
- **Sentence Transformers:** `all-MiniLM-L6-v2` model (384 dimensions, ~80MB) for local embeddings
- **Document Chunking:** Split on H1/H2 headers, preserve metadata (file path, section title)
- **LangGraph Integration:** New node in `lld_workflow` graph with typed State updates
- **CLI UX:** Spinner feedback during cold-boot model loading

## Security Considerations
- Vector store contains only internal documentation (no secrets)
- **Default mode (local embeddings):** Embedding model runs locally — no data leaves the machine
- **External API mode:** If user configures OpenAI/Gemini embedding APIs via environment variables, document text **will be sent to external services** for embedding generation. Users must explicitly opt-in by providing API keys.
- `.agentos/vector_store/` should be gitignored (local cache, regenerable)

## Files to Create/Modify
- `tools/rebuild_knowledge_base.py` — CLI tool to ingest docs into vector store
- `agentos/nodes/librarian.py` — RAG retrieval node implementation
- `agentos/workflows/lld/graph.py` — Wire Librarian into workflow graph
- `agentos/workflows/lld/state.py` — Add `retrieved_context` to State schema
- `pyproject.toml` — Add `chromadb`, `sentence-transformers` dependencies
- `.gitignore` — Add `.agentos/vector_store/`
- `docs/adrs/XXXX-rag-librarian.md` — Document architectural decision

## Dependencies
- None — this is a standalone enhancement to the LLD workflow

## Out of Scope (Future)
- **Automatic reindexing on file change** — requires file watcher, deferred
- **Remote/shared vector store** — team sync use case, not MVP
- **Query refinement/reranking** — single-stage retrieval sufficient for now
- **Cross-repository RAG** — multi-repo context is a separate feature
- **Semantic caching** — cache similar queries, optimization for later
- **Lightweight alternatives (FAISS + pickle)** — evaluate if ChromaDB proves too heavy

## Acceptance Criteria
- [ ] `tools/rebuild_knowledge_base.py` indexes `docs/` in < 10 seconds for 100+ files
- [ ] Query "How do I log errors?" retrieves logging-related standards/LLDs
- [ ] Query "authentication flow" retrieves identity/auth ADRs
- [ ] Librarian Node completes retrieval in < 500ms (after warm-up)
- [ ] Generated LLD references retrieved ADRs in "Constraints" section without manual prompting
- [ ] Workflow gracefully degrades when vector store missing (warning, not error)
- [ ] Manual `--context` flag still works and takes precedence over RAG results
- [ ] Vector store persists between sessions (no re-embedding on every run)
- [ ] Dependencies install cleanly on Linux/Mac/Windows CI environments
- [ ] CLI spinner displays during cold-boot model loading

## Definition of Done

### Implementation
- [ ] Core feature implemented
- [ ] Unit tests written and passing
- [ ] Integration test: end-to-end LLD generation with RAG

### Tools
- [ ] `tools/rebuild_knowledge_base.py` created with `--full` and `--incremental` modes
- [ ] Document tool usage in script header and `--help`

### Technical Verification
- [ ] Verify `pyproject.toml` changes pass CI on Linux/Mac/Windows
- [ ] Document any `chromadb`/`pydantic`/`sqlite` compatibility notes in README

### Documentation
- [ ] Update LLD Workflow wiki page with Librarian Node
- [ ] Update README.md with RAG setup instructions (including data residency note for external APIs)
- [ ] Create `docs/adrs/XXXX-rag-librarian.md`
- [ ] Add new files to `docs/0003-file-inventory.md`

### Reports (Pre-Merge Gate)
- [ ] `docs/reports/{IssueID}/implementation-report.md` created
- [ ] `docs/reports/{IssueID}/test-report.md` created

### Verification
- [ ] Run 0809 Security Audit - PASS
- [ ] Run 0817 Wiki Alignment Audit - PASS

## Testing Notes

**To test RAG retrieval quality:**
```bash
# Rebuild knowledge base
python tools/rebuild_knowledge_base.py --full

# Test queries manually
python -c "
from agentos.nodes.librarian import query_knowledge_base
results = query_knowledge_base('How should I implement logging?')
for r in results:
    print(f'{r.score:.2f} | {r.file_path} | {r.section}')
"
```

**To test graceful degradation:**
```bash
# Remove vector store
rm -rf .agentos/vector_store/

# Run LLD workflow — should warn but not fail
agentos lld create --brief "Test brief"
```

**To test manual override precedence:**
```bash
# Provide conflicting manual context
agentos lld create \
  --brief "Implement logging" \
  --context docs/adrs/0001-unrelated.md

# Verify manual context appears first in Designer input
```

**To test dependency compatibility:**
```bash
# Fresh virtual environment test
python -m venv test_env
source test_env/bin/activate
pip install -e .
python -c "import chromadb; import sentence_transformers; print('OK')"
```

## Labels
`feature:rag`, `workflow:lld`, `enhancement`

## Effort Estimate
**Large (L)** — 5-8 story points due to integration testing complexity and dependency verification across platforms.

## Original Brief
# RAG Injection: Architectural Consistency (The Librarian)

**Context:** We have implemented manual context injection via the `--context` CLI flag in the LLD Workflow (#DN-001). While useful, this relies entirely on the user remembering which ADRs or Standards are relevant. As the documentation grows (currently 100+ files), human memory becomes the bottleneck.

## Problem

**The "Amnesiac Designer" Failure Mode:**
When the Designer Node creates an LLD, it often proposes solutions that violate established architectural decisions because it cannot "see" the `docs/adrs/` folder.

* *Example:* Designer proposes a new logging library, ignoring `docs/LLDs/done/57-distributed-logging.md`.
* *Example:* Designer suggests direct SQL queries, ignoring `docs/adrs/0204-single-identity-orchestration.md`.

## Goal

Implement an **Automated Retrieval Node ("The Librarian")** at the start of the LLD Workflow.

1. **Index:** Automatically ingest `docs/adrs/`, `docs/standards/`, and `docs/LLDs/done/` into a local vector store.
2. **Retrieve:** Before the Designer starts, query the store with the Issue Brief.
3. **Inject:** Silently append the Top-3 most relevant governance documents to the context.

## Proposed Architecture

### 1. Local Vector Infrastructure

We will use **ChromaDB** (local, file-based) or **FAISS** to avoid external dependencies/infrastructure costs.

* **Storage Location:** `.agentos/vector_store/`
* **Ingestion Tool:** `tools/rebuild_knowledge_base.py`
* Scans `docs/` for markdown files.
* Splits by header (H1/H2).
* Generates embeddings (using a small local model like `all-MiniLM-L6-v2` or OpenAI/Gemini embeddings if API key available).



### 2. The Librarian Node (`agentos/nodes/librarian.py`)

A new node for the `lld_workflow` graph.

* **Input:** `issue_brief` (text)
* **Process:**
1. Embed the brief.
2. Query Vector Store for `k=3` nearest neighbors from `docs/adrs/` and `docs/standards/`.
3. Filter results (score threshold > 0.7).


* **Output:** `retrieved_context` (List of file paths + content snippets).

### 3. Workflow Integration

Modify `agentos/workflows/lld/graph.py`:

**Current:**
`Load Brief -> [Manual Context] -> Designer -> ...`

**New:**
`Load Brief -> [Librarian Node] -> [Manual Context Merge] -> Designer -> ...`

* The Librarian *augments* the manual `--context` flag, it does not replace it. User manual overrides always win.

## Implementation Steps

1. **Dependencies:** Add `chromadb` and `sentence-transformers` to `pyproject.toml`.
2. **Ingestion Script:** Create `tools/rebuild_knowledge_base.py`.
3. **Node Logic:** Implement `agentos/nodes/librarian.py`.
4. **Graph Update:** Wire the node into `run_lld_workflow.py`.

## Success Criteria

* [ ] `tools/rebuild_knowledge_base.py` runs in < 10 seconds for current docset.
* [ ] Querying "How do I log errors?" retrieves `docs/standards/0002-coding-standards.md` or `agentos/core/audit.py`.
* [ ] The generated LLD references the retrieved ADRs in its "Constraints" section without human prompting.