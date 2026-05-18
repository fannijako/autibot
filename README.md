# Autibot
RAG based chatbot trained on autism specific documents

## How to run the project

1. Clone the repository
2. Create Astra DB instance with an autibot database and a documents collection within it
3. Load the documents into the documents collection
4. Save the token in the .env file
5. Set the database API address in the .env file
6. Create a Discord app on the Discord developer portal
7. Set the token in the .env file
8. Add the App to the server
9. Create a Hugging Face account
10. Set the token in the .env file
11. Compose the docker container
12. Start chatting :)

```.env
DISCORD_TOKEN="<your-discord-app-token>"
HUGGINGFACE_TOKEN="<your-huggingface-token>"
ASTRA_DB_TOKEN="<your-astra-db-token>"
ASTRA_DB_API_ENDPOINT="https://<your-namespace>.apps.astra.datastax.com"
```

```bash
git clone https://github.com/fannijako/autibot.git
cd autibot
docker compose up --build
```

## Components

- **Discord App**: The app that allows the user to chat with the bot
- **Astra DB**: The database that stores the documents and the chat history
- **Hugging Face**: The model that is used to generate the responses

## Costs

- **Astra DB**: currently using a free tier
- **Hugging Face**: currently using a free tier

## RAG design

### Chunking

Chunking happens **upstream of this repository**. The `documents` collection
in Astra DB is populated externally (manual ingestion or a separate ETL job),
and each row stores a pre-chunked text passage. There is no in-repo splitter.

Practical guidance for whoever loads the collection: keep passages roughly
300–800 tokens with ~50 token overlap so a single passage fits comfortably in
the prompt window alongside the chat history and instructions. Source: autism
documents are mostly Hungarian-language guideline PDFs, so paragraph-aware
splitting (rather than fixed-character) preserves clinical phrasing.

### Embeddings

Embeddings are produced **server-side by Astra DB** via the `$vectorize`
operator. The embedding model is configured on the collection itself when it
is created in the Astra UI (e.g. NVIDIA `NV-Embed-QA` or an OpenAI model that
Astra proxies), *not* in this codebase. This is why no embedding model
dependency appears in `pyproject.toml`.

Why this choice: collection-managed `$vectorize` removes the need to run a
local embedding service or pay per-call to a third-party embeddings API, and
ensures query embeddings always match document embeddings (same model on both
sides, enforced by Astra).

### Vector store — Astra DB

- **Free serverless tier** — fits the project's cost profile (see
  [Costs](#costs)).
- **Built-in `$vectorize`** — single API for both storage and embedding;
  removes a moving part vs. Chroma / Qdrant / pgvector, which all require a
  separately-managed embedding pipeline.
- **Managed** — no infrastructure to operate; the alternative self-hosted
  stores would need a VPS or container.

The trade-off is vendor lock-in to DataStax's Data API. Migrating away would
require regenerating embeddings with whichever model the new store supports.

### Retrieval parameters

Defined in `app/vector_db.py`:

| Param          | Value | Where                                |
| -------------- | ----- | ------------------------------------ |
| `limit` (top-k) | 10    | `similarity_search` / `get_information_to_query` |
| `threshold`    | 0.6   | `filter_on_similarity`               |

The pipeline pulls the top 10 most similar passages, then drops anything below
cosine similarity 0.6. With sparse / poorly-matched queries this can yield an
empty context, which the LLM is instructed to handle gracefully (see prompt
below).

### LLM & prompt template

- **Model**: `HuggingFaceH4/zephyr-7b-beta` (see `app/utils.py:MODEL_ID`),
  served via `HuggingFaceEndpoint` with `max_new_tokens=512` and
  `streaming=True`.
- **Tokenizer**: the model's own tokenizer applies the chat template, so
  prompt formatting matches what Zephyr was instruction-tuned on.
- **Language**: Hungarian. System and user messages are both Hungarian, and
  the prompt explicitly asks for Hungarian replies.

The two-message template (`app/llm.py:format_prompt`) is:

- **system** — establishes the assistant's role: an AI helper for autistic
  people and their families, answering from a curated database.
- **user** — interpolates:
  - retrieved context (joined `$vectorize` text of the filtered passages),
  - rolling chat history (per-user, see below),
  - the current query,
  - and four explicit rules: answer only the question, reply in Hungarian
    with complete sentences, don't start a sentence you can't finish, and
    cite the official document when relevant.

### Conversation history

In-memory only (`collections.defaultdict` keyed by Discord `user_id`). Default
limits: **10 messages** per user, **1-hour** sliding expiry. Cleared
automatically on expiry, manually via `!clear_history`. History resets when
the container restarts — this is intentional for a free-tier bot but means
long-running threads lose context across deploys.

### Hallucination mitigation

Layered, in order of strength:

1. **Similarity floor (0.6)** — passages the embedding model considers
   weakly related are dropped before they reach the LLM.
2. **Closed-book instruction** — the user prompt tells the model to answer
   *only* from the supplied context and not to add anything beyond the
   answer to the question.
3. **Source-citation nudge** — the prompt asks the model to cite the
   official document when relevant, which makes unsupported claims more
   visible to the reader.
4. **Sentence-completeness rule** — instruction not to start sentences it
   cannot finish, reducing token-budget-induced fabrication at the 512-token
   ceiling.

Not (yet) implemented: explicit refusal when retrieval returns nothing,
confidence-score surfacing to the user, or an LLM-as-judge faithfulness
check. See `MAINTENANCE.md` for the planned `eval/` work.

### Why custom RAG instead of LangChain / LlamaIndex?

This project uses one small piece of LangChain — `langchain-huggingface`'s
`HuggingFaceEndpoint` as a thin client to the HF Inference API — and nothing
else. The retrieval, prompt assembly, and history handling are written
directly against `astrapy` and the tokenizer (see `app/vector_db.py`,
`app/llm.py`, `app/chatbot.py`). The choice is deliberate.

**What the frameworks would buy:**
- Chains / agents / tool-use orchestration
- Pluggable vector-store and embedding abstractions
- Prebuilt RAG patterns (`RetrievalQA`, query rewriting, multi-query)
- Tracing / callback infrastructure (LangSmith, etc.)

**Why we don't need them here:**
1. **The pipeline is linear and small.** Embed-via-Astra → top-k → threshold
   filter → format prompt → invoke LLM. Five steps, no branching. A framework
   chain would replace ~50 readable lines with an opaque object graph.
2. **Astra `$vectorize` already abstracts embedding.** The single point a
   framework's `VectorStore` interface would help — swapping embedding
   models — is handled server-side by the collection config. There is
   nothing to abstract over.
3. **Hungarian-language prompt is bespoke.** The system/user template
   (`app/llm.py:format_prompt`) is hand-tuned for Hungarian phrasing and
   citation rules; framework-default English templates would have to be
   overridden anyway.
4. **Debuggability.** Every step appears in `app/` source and in the project's
   log file. Framework callbacks would push the same information into a
   trace UI or behind layered wrappers — useful in a multi-chain system,
   noise here.
5. **Dependency surface.** `langchain` + `langchain-community` would pull in
   dozens of optional integrations and a fast-moving API. A bot that only
   needs an HTTP client to HF and an HTTP client to Astra doesn't need that
   churn — relevant for a free-tier deployment with no dedicated maintainer
   time for breaking-change upgrades.

**When this calculus would flip:** if the bot grew tool-use (function
calling, web search), multi-step reasoning, or needed to support multiple
vector stores / embedding models behind a stable interface, LlamaIndex or
LangGraph would start paying for itself. None of that is on the roadmap.
