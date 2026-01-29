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

## Requirements

### Vector Infrastructure
1. Use ChromaDB for local, file-based vector storage (no external dependencies)
2. Store vector database in `.agentos/vector_store/`
3. Support embedding models: `all-MiniLM-L6-v2` (default/local) or OpenAI/Gemini if API key available
4. Index all markdown files in `docs/adrs/`, `docs/standards/`, and `docs/LLDs/done/`
5. Split documents by H1/H2 headers for granular retrieval

### Librarian Node
1. Accept `issue_brief` text as input
2. Query vector store for k=5 candidates, return top 3 after filtering
3. Apply similarity score threshold of 0.7 (configurable)
4. Return list of `{file_path, section, content_snippet, score}`
5. Complete retrieval in < 500ms for typical queries

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

## Technical Approach
- **ChromaDB:** Persistent local vector store with HNSW index for fast similarity search
- **Sentence Transformers:** `all-MiniLM-L6-v2` model (384 dimensions, ~80MB) for local embeddings
- **Document Chunking:** Split on H1/H2 headers, preserve metadata (file path, section title)
- **LangGraph Integration:** New node in `lld_workflow` graph with typed State updates

## Security Considerations
- Vector store contains only internal documentation (no secrets)
- Embedding model runs locally — no data leaves the machine
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

## Acceptance Criteria
- [ ] `tools/rebuild_knowledge_base.py` indexes `docs/` in < 10 seconds for 100+ files
- [ ] Query "How do I log errors?" retrieves logging-related standards/LLDs
- [ ] Query "authentication flow" retrieves identity/auth ADRs
- [ ] Librarian Node completes retrieval in < 500ms
- [ ] Generated LLD references retrieved ADRs in "Constraints" section without manual prompting
- [ ] Workflow gracefully degrades when vector store missing (warning, not error)
- [ ] Manual `--context` flag still works and takes precedence over RAG results
- [ ] Vector store persists between sessions (no re-embedding on every run)

## Definition of Done

### Implementation
- [ ] Core feature implemented
- [ ] Unit tests written and passing
- [ ] Integration test: end-to-end LLD generation with RAG

### Tools
- [ ] `tools/rebuild_knowledge_base.py` created with `--full` and `--incremental` modes
- [ ] Document tool usage in script header and `--help`

### Documentation
- [ ] Update LLD Workflow wiki page with Librarian Node
- [ ] Update README.md with RAG setup instructions
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