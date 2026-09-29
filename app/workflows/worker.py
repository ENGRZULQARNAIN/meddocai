"""
Entry point for the Temporal worker process: connects to the Temporal
server, registers the document pipeline workflow and its activities,
then polls the task queue for work. This is the process that scales
horizontally — run more replicas and Temporal spreads work across them,
no extra code required.
"""
import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from app.core.config import get_settings
from app.workers.activities import (
    chunk_text,
    embed_chunks,
    extract_text,
    notify_complete,
)
from app.workflows.document_pipeline import DocumentPipelineWorkflow

logger = logging.getLogger(__name__)

TASK_QUEUE = "meddocai-documents"


async def main() -> None:
    settings = get_settings()
    client = await Client.connect(settings.temporal_host)

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[DocumentPipelineWorkflow],
        activities=[extract_text, chunk_text, embed_chunks, notify_complete],
    )

    logger.info("Temporal worker polling task queue %r", TASK_QUEUE)
    await worker.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
