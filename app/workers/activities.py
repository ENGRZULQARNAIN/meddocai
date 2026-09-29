"""
Temporal activities: the actual units of I/O/work that a workflow calls.

This replaces what used to be Celery tasks. The difference isn't the
function body — it's who's supervising it: Temporal persists that this
activity started, retries it on failure per `retry_policy` (below,
configured where it's called in document_pipeline.py), and the workflow
survives a worker crash without losing track of which activities already
completed.

Keep activities as plain, focused functions — no direct DB writes for
workflow *state* here (that's Temporal's job, via the workflow's history);
DB writes for *application* data (e.g. mirroring status onto the
`documents` row so `GET /documents/{id}` stays a cheap Postgres read) are
fine and expected.
"""
from temporalio import activity


@activity.defn
async def extract_text(document_id: str) -> None:
    """Extract raw text (OCR if the source is scanned) for a document."""
    raise NotImplementedError


@activity.defn
async def chunk_text(document_id: str) -> None:
    """Split extracted text into embeddable chunks."""
    raise NotImplementedError


@activity.defn
async def embed_chunks(document_id: str) -> None:
    """Generate and persist embeddings for a document's chunks."""
    raise NotImplementedError


@activity.defn
async def notify_complete(document_id: str) -> None:
    """Notify whoever's waiting that the pipeline finished."""
    raise NotImplementedError
