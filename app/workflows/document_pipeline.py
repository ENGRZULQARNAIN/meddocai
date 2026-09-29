"""
The durable, multi-step workflow for a single document: extract ->
chunk -> embed -> quality check -> (optional human review) -> notify.

Each step is a Temporal activity (app/workers/activities.py); Temporal
persists progress after every step so the workflow survives a worker
crash and resumes where it left off, and its execution history doubles
as an audit trail of what happened to this specific document.

Workflow code itself must stay deterministic — no direct I/O, no
`datetime.now()`, no random(). All real work (DB, network, filesystem)
happens inside activities, which the workflow just calls and awaits.
"""
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from app.workers.activities import (
        chunk_text,
        embed_chunks,
        extract_text,
        notify_complete,
    )

DEFAULT_RETRY_POLICY = RetryPolicy(
    initial_interval=timedelta(seconds=5),
    backoff_coefficient=2.0,
    maximum_interval=timedelta(minutes=5),
    maximum_attempts=5,
)


@workflow.defn
class DocumentPipelineWorkflow:
    @workflow.run
    async def run(self, document_id: str) -> None:
        activity_kwargs = dict(
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=DEFAULT_RETRY_POLICY,
        )

        await workflow.execute_activity(
            extract_text, document_id, **activity_kwargs
        )
        await workflow.execute_activity(
            chunk_text, document_id, **activity_kwargs
        )
        await workflow.execute_activity(
            embed_chunks, document_id, **activity_kwargs
        )
        await workflow.execute_activity(
            notify_complete, document_id, **activity_kwargs
        )
