# Backend Agent-RAG Graph Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the monolithic deterministic audit orchestration with an explicit, dependency-free Agent-RAG state graph while preserving current experiment outputs.

**Architecture:** Introduce a typed `ReviewAuditState`, pure retrieval/verification/ranking nodes, and a fixed `ReviewAuditGraph` executor. Keep the existing deterministic workflow function as the stable compatibility entrypoint, but delegate execution to the graph and return an explicit agent trace for backend observability and future provider/retriever substitutions.

**Tech Stack:** Python 3.14 standard library, dataclasses, existing EviReview core retrieval/verifier/ranker modules, SQLite worker, `unittest`.

---

## Scope Boundaries

- Freeze frontend work.
- Add explicit graph state, pure nodes, ordered transitions, and node trace.
- Preserve existing `workflow`, retrieval, verification, ranking, and metric-boundary outputs.
- Route worker execution through the graph compatibility entrypoint.
- Do not add LangGraph dependency, provider calls, Qdrant, or alter committed experiment metrics.

### Task 1: Lock graph execution behavior

- [x] Write failing core tests for state transitions, ordered node trace, and output compatibility.
- [x] Confirm RED because graph modules do not exist.

### Task 2: Implement graph state and nodes

- [x] Add `ReviewAuditState` with immutable inputs and mutable stage outputs.
- [x] Add pure retrieval, verification, and ranking nodes.
- [x] Add `ReviewAuditGraph` with explicit ordered transitions and failure context.
- [x] Delegate `run_deterministic_review_audit` to the graph.
- [x] Confirm core tests GREEN.

### Task 3: Integrate backend worker and verify

- [x] Add worker regression coverage for persisted agent trace.
- [x] Run API, backend, core, and Redis/RQ integration tests.
- [x] Run compile, dependency, diff, and secret checks.
- [x] Write backend Agent-RAG graph progress documentation.
- [x] Create a Lore commit and push `main`.
