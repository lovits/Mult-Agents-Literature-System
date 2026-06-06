from __future__ import annotations

import unittest

from app.queue.rq_queue import RQQueueAdapter


class FakeQueue:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def enqueue(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return type("Job", (), {"id": kwargs["job_id"]})()


class RQQueueAdapterTest(unittest.TestCase):
    def test_enqueue_sends_only_sqlite_path_and_job_id(self) -> None:
        queue = FakeQueue()
        adapter = RQQueueAdapter(queue, "/tmp/backend.sqlite3")

        delivery_id = adapter.enqueue("job-1")

        args, kwargs = queue.calls[0]
        self.assertEqual(args[1:], ("/tmp/backend.sqlite3", "job-1"))
        self.assertEqual(kwargs["job_id"], "rq-job-1")
        self.assertEqual(delivery_id, "rq-job-1")


if __name__ == "__main__":
    unittest.main()
