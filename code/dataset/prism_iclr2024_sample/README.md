# PRISM/OpenReview ICLR 2024 Sample

This folder contains a focused ICLR 2024 sample downloaded from the public OpenReview API.

## Contents

- `papers_manifest.csv`: metadata, decisions, local paths, and OpenReview URLs.
- `pdf/`: downloaded paper PDFs.
- `openreview_json/`: full OpenReview note JSON with direct replies.
- `reviews_txt/`: extracted human reviews, meta-reviews, decisions, and abstracts.
- `md_mineru_v4/`: high-quality Markdown converted with MinerU v4 precise API.

## Selection

The script selects a balanced accepted/rejected sample using keywords related to LLMs, retrieval, agents, reasoning, benchmarks, NLP, and evaluation. If needed, it backfills with other accepted/rejected ICLR 2024 submissions.

## Source

- OpenReview API v2: https://api2.openreview.net/notes
- Venue invitation: ICLR.cc/2024/Conference/-/Submission

## Markdown Conversion Note

MinerU v4 precise API conversion is complete for all 50 PDFs. Use `md_mineru_v4/` as the primary Markdown source for Paper-RAG indexing.

Intermediate conversion folders, ZIP caches, fallback Markdown, and helper scripts were removed so this dataset folder keeps only the files needed for the thesis experiments.
