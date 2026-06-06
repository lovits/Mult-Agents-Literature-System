# Graph Registry And Ablation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Agent-RAG node profiles configurable and produce reproducible full/no-verifier/no-ranker ablation metrics without manual labels.

**Architecture:** Add a core graph profile registry with explicit node tuples. Implement transparent ablation nodes that either assume support or preserve candidate order. Run all profiles on the same local rubric-agent weaknesses and score selected findings against the full graph's silver verifier reference.

**Tech Stack:** Python standard library, dataclasses, unittest, existing EviReview core and experiment artifacts.

---

## Tasks

1. Write RED tests for profile lookup, unknown profiles, no-verifier, and no-ranker behavior.
2. Implement registry and ablation nodes while preserving the default graph API.
3. Add a graph ablation experiment script and validator.
4. Export ablation metrics through Phase 2H-A.
5. Run full regression, document, commit, and push.
