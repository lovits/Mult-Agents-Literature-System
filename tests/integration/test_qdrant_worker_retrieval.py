from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from redis import Redis
from rq import Queue, SimpleWorker

from app.queue.rq_queue import RQQueueAdapter
from app.repositories.sqlite_run_repository import SQLiteRunRepository
from app.schemas.runs import ReviewAuditRequest
from app.services.review_audit_service import ReviewAuditService
from evireview_core.domain.models import EvidenceBlock, Weakness
from services.worker.tasks.review_audit import run_next_job


@unittest.skipUnless(os.getenv("EVIREVIEW_QDRANT_INTEGRATION") == "1", "requires local Qdrant")
class QdrantWorkerIntegrationTest(unittest.TestCase):
    def test_worker_runs_complete_audit_with_qdrant_sparse_retrieval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repository = SQLiteRunRepository(Path(tmp) / "qdrant.sqlite3")
            repository.initialize()
            service = ReviewAuditService(repository)
            created = service.create_review_audit(
                ReviewAuditRequest(
                    paper_id="qdrant-integration",
                    weaknesses=[
                        Weakness(
                            "w1",
                            "qdrant-integration",
                            "The evaluation lacks an ablation study.",
                            "experiment",
                            "major",
                        )
                    ],
                    evidence_blocks=[
                        EvidenceBlock(
                            "b1",
                            "qdrant-integration",
                            "Experiments",
                            "experiment",
                            "The evaluation reports accuracy but does not include an ablation study.",
                        ),
                        EvidenceBlock(
                            "b2",
                            "qdrant-integration",
                            "Method",
                            "method",
                            "The method uses a retrieval planner and verifier.",
                        ),
                    ],
                    retriever="qdrant_sparse",
                    finding_top_k=1,
                )
            )

            execution = run_next_job(repository)
            result = repository.get_run(created["run"]["run_id"])["result"]

        self.assertEqual(execution["status"], "succeeded")
        self.assertEqual(result["retrieval"]["w1"][0]["block_id"], "b1")
        self.assertEqual(result["retrieval"]["w1"][0]["retriever"], "qdrant_sparse")
        self.assertEqual(result["agent_trace"][-3]["node"], "deduplicate_weaknesses")
        self.assertTrue(result["auxiliary_decision"]["not_for_decision"])

    @unittest.skipUnless(os.getenv("EVIREVIEW_REDIS_INTEGRATION") == "1", "requires local Redis")
    def test_rq_worker_executes_persisted_qdrant_sparse_audit(self) -> None:
        connection = Redis.from_url(os.environ["EVIREVIEW_REDIS_URL"])
        connection.flushdb()
        queue = Queue("evireview-qdrant-integration", connection=connection)
        with tempfile.TemporaryDirectory() as tmp:
            sqlite_path = Path(tmp) / "qdrant-rq.sqlite3"
            repository = SQLiteRunRepository(sqlite_path)
            repository.initialize()
            service = ReviewAuditService(repository, RQQueueAdapter(queue, str(sqlite_path)))
            created = service.create_and_enqueue(
                ReviewAuditRequest(
                    paper_id="qdrant-rq-integration",
                    weaknesses=[
                        Weakness("w1", "qdrant-rq-integration", "The evaluation lacks ablation.", "experiment", "major")
                    ],
                    evidence_blocks=[
                        EvidenceBlock(
                            "b1",
                            "qdrant-rq-integration",
                            "Experiments",
                            "experiment",
                            "The evaluation contains no ablation.",
                        )
                    ],
                    retriever="qdrant_sparse",
                )
            )

            SimpleWorker([queue], connection=connection).work(burst=True)
            result = repository.get_run(created["run"]["run_id"])["result"]

        self.assertEqual(result["retriever"], "qdrant_sparse")
        self.assertEqual(result["retrieval"]["w1"][0]["block_id"], "b1")
        self.assertEqual(queue.count, 0)
        connection.flushdb()

    def test_worker_executes_qdrant_hybrid_with_environment_embedding_adapter(self) -> None:
        def embedding_transport(_url, _headers, payload):
            return {
                "data": [
                    {
                        "index": index,
                        "embedding": [1.0, 0.0] if "ablation" in text.lower() else [0.0, 1.0],
                    }
                    for index, text in enumerate(payload["input"])
                ]
            }

        with tempfile.TemporaryDirectory() as tmp:
            repository = SQLiteRunRepository(Path(tmp) / "qdrant-hybrid.sqlite3")
            repository.initialize()
            service = ReviewAuditService(repository)
            created = service.create_review_audit(
                ReviewAuditRequest(
                    paper_id="qdrant-hybrid-integration",
                    weaknesses=[
                        Weakness("w1", "qdrant-hybrid-integration", "The evaluation lacks ablation.", "experiment", "major")
                    ],
                    evidence_blocks=[
                        EvidenceBlock(
                            "b1",
                            "qdrant-hybrid-integration",
                            "Experiments",
                            "experiment",
                            "The evaluation contains no ablation.",
                        ),
                        EvidenceBlock(
                            "b2",
                            "qdrant-hybrid-integration",
                            "Method",
                            "method",
                            "The method uses a retrieval planner.",
                        ),
                    ],
                    retriever="qdrant_hybrid",
                )
            )
            environment = {
                "EVIREVIEW_EMBEDDING_BASE_URL": "https://embedding.example/v1",
                "EVIREVIEW_EMBEDDING_API_KEY": "integration-secret",
                "EVIREVIEW_EMBEDDING_MODEL": "integration-embedder",
            }
            with patch.dict("os.environ", environment, clear=False):
                with patch("evireview_core.providers.embedding._urllib_transport", embedding_transport):
                    execution = run_next_job(repository)
            result = repository.get_run(created["run"]["run_id"])["result"]

        self.assertEqual(execution["status"], "succeeded")
        self.assertEqual(result["retrieval"]["w1"][0]["block_id"], "b1")
        self.assertEqual(result["retrieval"]["w1"][0]["retriever"], "qdrant_hybrid")


if __name__ == "__main__":
    unittest.main()
