# Chatbot Release Notes

## v2.1.1 — Security patch

No runtime behavior changes. Resolves open Dependabot alerts and an
implicit-dependency gap surfaced by the upgrade.

### Security fixes

- **pytest** `^8.0.0` → `^9.0.3` — GHSA-6w46-j5rx-g56g (medium, tmpdir
  handling).
- **pytest-asyncio** `^0.23.0` → `^1.3.0` — required for pytest 9
  compatibility.
- **langchain-huggingface** `^0.1.2` → `^1.2.2` — transitively pulls in
  `langchain-core` 1.4.0 and resolves:
  - GHSA-qh6h-p6c9-ff54 (high, path traversal in legacy `load_prompt`)
  - GHSA-2g6r-c272-w58r (low, SSRF via `image_url` token counting)
- **torch** floor raised to `>=2.8.0` — GHSA-887c-mr87-cxwp (medium,
  improper resource release). Locked at 2.12.0.

### Dependencies

- **transformers** added as a direct dependency (`^5.0.0`). Previously
  pulled in transitively by `langchain-huggingface 0.1.2`; on 1.2.2 it
  only ships under the `[full]` extra, and `app/llm.py` imports
  `AutoTokenizer` directly.
- Python constraint tightened from `^3.11` to `>=3.11,<3.15` to satisfy
  `triton`'s Python cap (transitive of the new torch). CI still covers
  3.11 and 3.12.

---

## v2.1.0 — Maintenance & developer experience

No runtime behavior changes. This release overhauls the project's build,
test, and documentation surface so future contributions land on a known
baseline.

### Tooling

- **Poetry** replaces `requirements.txt`. Version constraints live in
  `pyproject.toml`; `poetry.lock` (generated on first `poetry install`)
  pins exact versions for reproducible builds and Docker images.
- **Makefile** added with `install`, `lock`, `update`, `run`, `lint`,
  `pylint`, `flake8`, `test`, `docker-build`, `docker-up`, `docker-down`,
  and `clean` targets.
- **Dockerfile** now installs deps via Poetry against `pyproject.toml`.
- **`.flake8`** config excludes `.venv` and other vendored dirs from lint.
- **pylint config** centralized in `pyproject.toml` (`[tool.pylint."messages control"]`).

### Tests & CI

- `tests/` directory added with pytest-based coverage:
  - Retrieval unit tests (`tests/test_vector_db.py`)
  - Prompt-formatting unit tests (`tests/test_llm.py`)
  - ChatBot history + end-to-end mocked RAG flow (`tests/test_chatbot.py`)
- `pytest` + `pytest-asyncio` added as dev dependencies.
- New `Tests` GitHub Actions workflow runs the suite on push/PR against
  Python 3.11 and 3.12.
- `Pylint and flake8` workflow updated to use Poetry and the new Python
  matrix.

### Documentation

- **README** gains a "RAG design" section documenting chunking
  responsibility, Astra `$vectorize` embeddings, vector-store choice,
  retrieval params (top-k=10, threshold=0.6), the Hungarian prompt
  template, and layered hallucination mitigation.
- **README** gains a "Why custom RAG instead of LangChain / LlamaIndex?"
  section.
- **MAINTENANCE.md** tracks the remaining backlog (eval set, release tags,
  data-source documentation, etc.).

### Notes for operators

- Local setup now requires Poetry (`pipx install poetry` recommended).
- The Python floor moved to 3.11 (matches the Dockerfile); 3.9 and 3.10
  are no longer covered in CI.

---

## v2.0.0

### New Features

#### Conversation Management
- **Chat History**: Implemented per-user conversation tracking (short-term)
  - Short term history management for conversation-like interactions
  - Ability to clear or show the history
  - History is used in the RAG approach

#### New Commands
- `!clear_history`: Erases your current conversation history
- `!show_history`: Displays your active conversation thread

#### Enhanced Context Management
- Improved conversation coherence through:
  - RAG (Retrieval-Augmented Generation) integration
  - Contextual awareness from chat history
  - Natural conversation flow maintenance

### Technical Specifications

#### History Management
- **Expiration Rules**:
  - Messages automatically expire after 1 hour
  - Maximum 10 messages per user (configurable)
  - Automatic cleanup of expired messages

#### Storage Implementation
- In-memory storage system
  - Lightweight and fast
  - Dynamic memory management
  - Session-based persistence

### Important Notes

#### Usage Guidelines
1. Start chatting naturally - history is maintained automatically
2. View your conversation thread with `!show_history`
3. Reset your conversation using `!clear_history`

#### Limitations
- History is not persistent across bot restarts
- Memory usage scales with active user count

### Getting Started
Simply start a conversation with the bot - no additional setup required. Use the provided commands to manage your chat history as needed.

## v1.0.0

### Initial Release Features

#### Core Functionality
- Basic chatbot interactions
- Command-based interface
- Single-message context

#### RAG Integration
- Document-based knowledge retrieval
- Basic context injection
- Query-based information extraction

#### Commands
- Basic utility commands
- Help system
- Error handling

### Technical Details
- Stateless operation
- Simple request/response model
- No conversation persistence

### Limitations
- No conversation history
- Limited context awareness
- Single-turn interactions only

---
*For technical support or feature requests, please contact the development team.*