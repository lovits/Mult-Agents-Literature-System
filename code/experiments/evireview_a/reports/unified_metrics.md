# Unified Experiment Metrics

| Dataset | Task | Module | Method | Metric | Value | Boundary | Source artifact |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| CLAIMCHECK | groundedness | verifier | feature_verifier | accuracy | 0.5548 | diagnostic | claimcheck_feature_verifier_metrics.json |
| CLAIMCHECK | groundedness | verifier | feature_verifier | confusion.Grounded.Grounded | 67 | diagnostic | claimcheck_feature_verifier_metrics.json |
| CLAIMCHECK | groundedness | verifier | feature_verifier | confusion.Grounded.Ungrounded | 41 | diagnostic | claimcheck_feature_verifier_metrics.json |
| CLAIMCHECK | groundedness | verifier | feature_verifier | confusion.Ungrounded.Grounded | 28 | diagnostic | claimcheck_feature_verifier_metrics.json |
| CLAIMCHECK | groundedness | verifier | feature_verifier | confusion.Ungrounded.Ungrounded | 19 | diagnostic | claimcheck_feature_verifier_metrics.json |
| CLAIMCHECK | groundedness | verifier | feature_verifier | count | 155 | diagnostic | claimcheck_feature_verifier_metrics.json |
| CLAIMCHECK | groundedness | verifier | feature_verifier | macro_f1 | 0.5076 | diagnostic | claimcheck_feature_verifier_metrics.json |
| CLAIMCHECK | groundedness | verifier | feature_verifier | per_label.Grounded.f1 | 0.6601 | diagnostic | claimcheck_feature_verifier_metrics.json |
| CLAIMCHECK | groundedness | verifier | feature_verifier | per_label.Grounded.precision | 0.7053 | diagnostic | claimcheck_feature_verifier_metrics.json |
| CLAIMCHECK | groundedness | verifier | feature_verifier | per_label.Grounded.recall | 0.6204 | diagnostic | claimcheck_feature_verifier_metrics.json |
| CLAIMCHECK | groundedness | verifier | feature_verifier | per_label.Grounded.support | 108 | diagnostic | claimcheck_feature_verifier_metrics.json |
| CLAIMCHECK | groundedness | verifier | feature_verifier | per_label.Ungrounded.f1 | 0.3551 | diagnostic | claimcheck_feature_verifier_metrics.json |
| CLAIMCHECK | groundedness | verifier | feature_verifier | per_label.Ungrounded.precision | 0.3167 | diagnostic | claimcheck_feature_verifier_metrics.json |
| CLAIMCHECK | groundedness | verifier | feature_verifier | per_label.Ungrounded.recall | 0.4043 | diagnostic | claimcheck_feature_verifier_metrics.json |
| CLAIMCHECK | groundedness | verifier | feature_verifier | per_label.Ungrounded.support | 47 | diagnostic | claimcheck_feature_verifier_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | bm25_max_similarity | bottom1_ungrounded_rate | 0.6667 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | bm25_max_similarity | evaluated_group_count | 24 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | bm25_max_similarity | map | 0.7771 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | bm25_max_similarity | ndcg_at_3 | 0.7934 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | bm25_max_similarity | ndcg_at_5 | 0.8205 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | bm25_max_similarity | skipped_single_label_group_count | 30 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | bm25_max_similarity | top1_grounded_rate | 0.625 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | candidate_claim_count | bottom1_ungrounded_rate | 0.625 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | candidate_claim_count | evaluated_group_count | 24 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | candidate_claim_count | map | 0.7597 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | candidate_claim_count | ndcg_at_3 | 0.7806 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | candidate_claim_count | ndcg_at_5 | 0.8077 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | candidate_claim_count | skipped_single_label_group_count | 30 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | candidate_claim_count | top1_grounded_rate | 0.5833 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | embedding_max_similarity | bottom1_ungrounded_rate | 0.5833 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | embedding_max_similarity | evaluated_group_count | 24 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | embedding_max_similarity | map | 0.7502 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | embedding_max_similarity | ndcg_at_3 | 0.7632 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | embedding_max_similarity | ndcg_at_5 | 0.8193 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | embedding_max_similarity | skipped_single_label_group_count | 30 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | embedding_max_similarity | top1_grounded_rate | 0.5833 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | feature_verifier_probability | bottom1_ungrounded_rate | 0.5417 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | feature_verifier_probability | evaluated_group_count | 24 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | feature_verifier_probability | map | 0.7424 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | feature_verifier_probability | ndcg_at_3 | 0.7828 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | feature_verifier_probability | ndcg_at_5 | 0.8198 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | feature_verifier_probability | skipped_single_label_group_count | 30 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | ranker | evidence_ranker | feature_verifier_probability | top1_grounded_rate | 0.5833 | diagnostic | claimcheck_evidence_ranker_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_openrouter_rrf_hybrid | main.grounded_weakness_count | 108 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_openrouter_rrf_hybrid | main.hit_at_1 | 0.2361 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_openrouter_rrf_hybrid | main.hit_at_10 | 0.6806 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_openrouter_rrf_hybrid | main.hit_at_3 | 0.4306 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_openrouter_rrf_hybrid | main.hit_at_5 | 0.5556 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_openrouter_rrf_hybrid | main.mapped_target_count | 72 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_openrouter_rrf_hybrid | main.mrr | 0.3834 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_openrouter_rrf_hybrid | main.target_mapping_threshold | 0.7 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_openrouter_rrf_hybrid | main.unmapped_target_count | 36 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_openrouter_rrf_hybrid | pilot.grounded_weakness_count | 12 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_openrouter_rrf_hybrid | pilot.hit_at_1 | 0.5 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_openrouter_rrf_hybrid | pilot.hit_at_10 | 0.8333 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_openrouter_rrf_hybrid | pilot.hit_at_3 | 0.6667 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_openrouter_rrf_hybrid | pilot.hit_at_5 | 0.6667 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_openrouter_rrf_hybrid | pilot.mapped_target_count | 6 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_openrouter_rrf_hybrid | pilot.mrr | 0.578 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_openrouter_rrf_hybrid | pilot.target_mapping_threshold | 0.7 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_openrouter_rrf_hybrid | pilot.unmapped_target_count | 6 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_sparse | main.grounded_weakness_count | 108 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_sparse | main.hit_at_1 | 0.1806 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_sparse | main.hit_at_10 | 0.5833 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_sparse | main.hit_at_3 | 0.3611 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_sparse | main.hit_at_5 | 0.4167 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_sparse | main.mapped_target_count | 72 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_sparse | main.mrr | 0.3135 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_sparse | main.target_mapping_threshold | 0.7 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_sparse | main.unmapped_target_count | 36 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_sparse | pilot.grounded_weakness_count | 12 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_sparse | pilot.hit_at_1 | 0.5 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_sparse | pilot.hit_at_10 | 0.8333 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_sparse | pilot.hit_at_3 | 0.5 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_sparse | pilot.hit_at_5 | 0.5 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_sparse | pilot.mapped_target_count | 6 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_sparse | pilot.mrr | 0.5442 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_sparse | pilot.target_mapping_threshold | 0.7 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | bm25_sparse | pilot.unmapped_target_count | 6 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | openrouter_dense | main.grounded_weakness_count | 108 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | openrouter_dense | main.hit_at_1 | 0.2222 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | openrouter_dense | main.hit_at_10 | 0.7917 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | openrouter_dense | main.hit_at_3 | 0.5 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | openrouter_dense | main.hit_at_5 | 0.6944 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | openrouter_dense | main.mapped_target_count | 72 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | openrouter_dense | main.mrr | 0.4067 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | openrouter_dense | main.target_mapping_threshold | 0.7 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | openrouter_dense | main.unmapped_target_count | 36 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | openrouter_dense | pilot.grounded_weakness_count | 12 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | openrouter_dense | pilot.hit_at_1 | 0.3333 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | openrouter_dense | pilot.hit_at_10 | 0.6667 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | openrouter_dense | pilot.hit_at_3 | 0.6667 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | openrouter_dense | pilot.hit_at_5 | 0.6667 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | openrouter_dense | pilot.mapped_target_count | 6 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | openrouter_dense | pilot.mrr | 0.5184 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | openrouter_dense | pilot.target_mapping_threshold | 0.7 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag | openrouter_dense | pilot.unmapped_target_count | 6 | gold | dense_hybrid_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_openrouter_rrf_hybrid | main.grounded_weakness_count | 108 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_openrouter_rrf_hybrid | main.hit_at_1 | 0.2639 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_openrouter_rrf_hybrid | main.hit_at_10 | 0.7222 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_openrouter_rrf_hybrid | main.hit_at_3 | 0.4306 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_openrouter_rrf_hybrid | main.hit_at_5 | 0.5972 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_openrouter_rrf_hybrid | main.latency_ms_mean | 3.647 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_openrouter_rrf_hybrid | main.latency_ms_p50 | 3.606 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_openrouter_rrf_hybrid | main.latency_ms_p95 | 4.086 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_openrouter_rrf_hybrid | main.mapped_target_count | 72 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_openrouter_rrf_hybrid | main.mrr | 0.4039 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_openrouter_rrf_hybrid | main.unmapped_target_count | 36 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_openrouter_rrf_hybrid | pilot.grounded_weakness_count | 12 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_openrouter_rrf_hybrid | pilot.hit_at_1 | 0.6667 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_openrouter_rrf_hybrid | pilot.hit_at_10 | 0.6667 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_openrouter_rrf_hybrid | pilot.hit_at_3 | 0.6667 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_openrouter_rrf_hybrid | pilot.hit_at_5 | 0.6667 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_openrouter_rrf_hybrid | pilot.latency_ms_mean | 3.572 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_openrouter_rrf_hybrid | pilot.latency_ms_p50 | 3.542 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_openrouter_rrf_hybrid | pilot.latency_ms_p95 | 3.692 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_openrouter_rrf_hybrid | pilot.mapped_target_count | 6 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_openrouter_rrf_hybrid | pilot.mrr | 0.6841 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_openrouter_rrf_hybrid | pilot.unmapped_target_count | 6 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_sparse | main.grounded_weakness_count | 108 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_sparse | main.hit_at_1 | 0.1806 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_sparse | main.hit_at_10 | 0.5833 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_sparse | main.hit_at_3 | 0.3611 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_sparse | main.hit_at_5 | 0.4167 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_sparse | main.latency_ms_mean | 4.232 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_sparse | main.latency_ms_p50 | 4.033 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_sparse | main.latency_ms_p95 | 5.999 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_sparse | main.mapped_target_count | 72 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_sparse | main.mrr | 0.313 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_sparse | main.unmapped_target_count | 36 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_sparse | pilot.grounded_weakness_count | 12 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_sparse | pilot.hit_at_1 | 0.5 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_sparse | pilot.hit_at_10 | 0.8333 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_sparse | pilot.hit_at_3 | 0.5 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_sparse | pilot.hit_at_5 | 0.5 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_sparse | pilot.latency_ms_mean | 7.297 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_sparse | pilot.latency_ms_p50 | 5.206 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_sparse | pilot.latency_ms_p95 | 18.958 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_sparse | pilot.mapped_target_count | 6 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_sparse | pilot.mrr | 0.5442 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_bm25_sparse | pilot.unmapped_target_count | 6 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_openrouter_dense | main.grounded_weakness_count | 108 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_openrouter_dense | main.hit_at_1 | 0.2222 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_openrouter_dense | main.hit_at_10 | 0.7917 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_openrouter_dense | main.hit_at_3 | 0.5 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_openrouter_dense | main.hit_at_5 | 0.6944 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_openrouter_dense | main.latency_ms_mean | 4.406 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_openrouter_dense | main.latency_ms_p50 | 4.291 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_openrouter_dense | main.latency_ms_p95 | 6.791 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_openrouter_dense | main.mapped_target_count | 72 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_openrouter_dense | main.mrr | 0.4067 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_openrouter_dense | main.unmapped_target_count | 36 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_openrouter_dense | pilot.grounded_weakness_count | 12 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_openrouter_dense | pilot.hit_at_1 | 0.3333 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_openrouter_dense | pilot.hit_at_10 | 0.6667 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_openrouter_dense | pilot.hit_at_3 | 0.6667 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_openrouter_dense | pilot.hit_at_5 | 0.6667 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_openrouter_dense | pilot.latency_ms_mean | 5.613 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_openrouter_dense | pilot.latency_ms_p50 | 5.56 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_openrouter_dense | pilot.latency_ms_p95 | 6.813 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_openrouter_dense | pilot.mapped_target_count | 6 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_openrouter_dense | pilot.mrr | 0.5184 | gold | live_qdrant_retrieval_metrics.json |
| CLAIMCHECK | retrieval | paper_rag_qdrant | qdrant_openrouter_dense | pilot.unmapped_target_count | 6 | gold | live_qdrant_retrieval_metrics.json |
| Local OpenReview/PRISM | ablation | agent_rag_graph | full | mean_reference_support | 0.3632 | silver | graph_ablation_metrics.json |
| Local OpenReview/PRISM | ablation | agent_rag_graph | full | reference_partial_or_better_rate | 0.0355 | silver | graph_ablation_metrics.json |
| Local OpenReview/PRISM | ablation | agent_rag_graph | full | reference_unsupported_rate | 0.0 | silver | graph_ablation_metrics.json |
| Local OpenReview/PRISM | ablation | agent_rag_graph | full | selected_count | 141 | silver | graph_ablation_metrics.json |
| Local OpenReview/PRISM | ablation | agent_rag_graph | full | topk_overlap_with_full | 1.0 | silver | graph_ablation_metrics.json |
| Local OpenReview/PRISM | ablation | agent_rag_graph | no_ranker | mean_reference_support | 0.3583 | silver | graph_ablation_metrics.json |
| Local OpenReview/PRISM | ablation | agent_rag_graph | no_ranker | reference_partial_or_better_rate | 0.0142 | silver | graph_ablation_metrics.json |
| Local OpenReview/PRISM | ablation | agent_rag_graph | no_ranker | reference_unsupported_rate | 0.0 | silver | graph_ablation_metrics.json |
| Local OpenReview/PRISM | ablation | agent_rag_graph | no_ranker | selected_count | 141 | silver | graph_ablation_metrics.json |
| Local OpenReview/PRISM | ablation | agent_rag_graph | no_ranker | topk_overlap_with_full | 0.9078 | silver | graph_ablation_metrics.json |
| Local OpenReview/PRISM | ablation | agent_rag_graph | no_verifier | mean_reference_support | 0.3569 | silver | graph_ablation_metrics.json |
| Local OpenReview/PRISM | ablation | agent_rag_graph | no_verifier | reference_partial_or_better_rate | 0.0071 | silver | graph_ablation_metrics.json |
| Local OpenReview/PRISM | ablation | agent_rag_graph | no_verifier | reference_unsupported_rate | 0.0 | silver | graph_ablation_metrics.json |
| Local OpenReview/PRISM | ablation | agent_rag_graph | no_verifier | selected_count | 141 | silver | graph_ablation_metrics.json |
| Local OpenReview/PRISM | ablation | agent_rag_graph | no_verifier | topk_overlap_with_full | 0.9362 | silver | graph_ablation_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 0.aggregate.accuracy | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 0.aggregate.confusion.Accept.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 0.aggregate.confusion.Accept.Reject | 20 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 0.aggregate.confusion.Reject.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 0.aggregate.confusion.Reject.Reject | 20 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 0.aggregate.count | 50 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 0.aggregate.macro_f1 | 0.4505 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 0.aggregate.per_label.Accept.f1 | 0.2857 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 0.aggregate.per_label.Accept.precision | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 0.aggregate.per_label.Accept.recall | 0.2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 0.aggregate.per_label.Accept.support | 25 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 0.aggregate.per_label.Reject.f1 | 0.6154 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 0.aggregate.per_label.Reject.precision | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 0.aggregate.per_label.Reject.recall | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 0.aggregate.per_label.Reject.support | 25 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 0.aggregate.roc_auc | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 0.feature_count | 0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 0.fold_macro_f1_mean | 0.3333 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 0.fold_macro_f1_std | 0.0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 1.aggregate.accuracy | 0.68 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 1.aggregate.confusion.Accept.Accept | 17 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 1.aggregate.confusion.Accept.Reject | 8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 1.aggregate.confusion.Reject.Accept | 8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 1.aggregate.confusion.Reject.Reject | 17 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 1.aggregate.count | 50 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 1.aggregate.macro_f1 | 0.68 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 1.aggregate.per_label.Accept.f1 | 0.68 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 1.aggregate.per_label.Accept.precision | 0.68 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 1.aggregate.per_label.Accept.recall | 0.68 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 1.aggregate.per_label.Accept.support | 25 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 1.aggregate.per_label.Reject.f1 | 0.68 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 1.aggregate.per_label.Reject.precision | 0.68 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 1.aggregate.per_label.Reject.recall | 0.68 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 1.aggregate.per_label.Reject.support | 25 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 1.aggregate.roc_auc | 0.6896 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 1.feature_count | 7 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 1.fold_macro_f1_mean | 0.6755 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 1.fold_macro_f1_std | 0.0783 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 2.aggregate.accuracy | 0.62 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 2.aggregate.confusion.Accept.Accept | 16 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 2.aggregate.confusion.Accept.Reject | 9 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 2.aggregate.confusion.Reject.Accept | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 2.aggregate.confusion.Reject.Reject | 15 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 2.aggregate.count | 50 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 2.aggregate.macro_f1 | 0.6198 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 2.aggregate.per_label.Accept.f1 | 0.6275 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 2.aggregate.per_label.Accept.precision | 0.6154 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 2.aggregate.per_label.Accept.recall | 0.64 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 2.aggregate.per_label.Accept.support | 25 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 2.aggregate.per_label.Reject.f1 | 0.6122 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 2.aggregate.per_label.Reject.precision | 0.625 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 2.aggregate.per_label.Reject.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 2.aggregate.per_label.Reject.support | 25 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 2.aggregate.roc_auc | 0.6512 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 2.feature_count | 11 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 2.fold_macro_f1_mean | 0.5822 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 2.fold_macro_f1_std | 0.1983 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 3.aggregate.accuracy | 0.44 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 3.aggregate.confusion.Accept.Accept | 7 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 3.aggregate.confusion.Accept.Reject | 18 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 3.aggregate.confusion.Reject.Accept | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 3.aggregate.confusion.Reject.Reject | 15 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 3.aggregate.count | 50 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 3.aggregate.macro_f1 | 0.4253 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 3.aggregate.per_label.Accept.f1 | 0.3333 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 3.aggregate.per_label.Accept.precision | 0.4118 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 3.aggregate.per_label.Accept.recall | 0.28 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 3.aggregate.per_label.Accept.support | 25 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 3.aggregate.per_label.Reject.f1 | 0.5172 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 3.aggregate.per_label.Reject.precision | 0.4545 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 3.aggregate.per_label.Reject.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 3.aggregate.per_label.Reject.support | 25 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 3.aggregate.roc_auc | 0.448 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 3.feature_count | 9 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 3.fold_macro_f1_mean | 0.3884 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 3.fold_macro_f1_std | 0.1298 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 4.aggregate.accuracy | 0.64 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 4.aggregate.confusion.Accept.Accept | 16 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 4.aggregate.confusion.Accept.Reject | 9 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 4.aggregate.confusion.Reject.Accept | 9 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 4.aggregate.confusion.Reject.Reject | 16 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 4.aggregate.count | 50 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 4.aggregate.macro_f1 | 0.64 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 4.aggregate.per_label.Accept.f1 | 0.64 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 4.aggregate.per_label.Accept.precision | 0.64 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 4.aggregate.per_label.Accept.recall | 0.64 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 4.aggregate.per_label.Accept.support | 25 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 4.aggregate.per_label.Reject.f1 | 0.64 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 4.aggregate.per_label.Reject.precision | 0.64 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 4.aggregate.per_label.Reject.recall | 0.64 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 4.aggregate.per_label.Reject.support | 25 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 4.aggregate.roc_auc | 0.6736 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 4.feature_count | 18 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 4.fold_macro_f1_mean | 0.6318 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 4.fold_macro_f1_std | 0.1492 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 5.aggregate.accuracy | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 5.aggregate.confusion.Accept.Accept | 14 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 5.aggregate.confusion.Accept.Reject | 11 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 5.aggregate.confusion.Reject.Accept | 9 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 5.aggregate.confusion.Reject.Reject | 16 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 5.aggregate.count | 50 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 5.aggregate.macro_f1 | 0.5994 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 5.aggregate.per_label.Accept.f1 | 0.5833 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 5.aggregate.per_label.Accept.precision | 0.6087 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 5.aggregate.per_label.Accept.recall | 0.56 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 5.aggregate.per_label.Accept.support | 25 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 5.aggregate.per_label.Reject.f1 | 0.6154 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 5.aggregate.per_label.Reject.precision | 0.5926 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 5.aggregate.per_label.Reject.recall | 0.64 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 5.aggregate.per_label.Reject.support | 25 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 5.aggregate.roc_auc | 0.6704 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 5.feature_count | 16 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 5.fold_macro_f1_mean | 0.5968 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 5.fold_macro_f1_std | 0.0904 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 6.aggregate.accuracy | 0.58 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 6.aggregate.confusion.Accept.Accept | 13 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 6.aggregate.confusion.Accept.Reject | 12 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 6.aggregate.confusion.Reject.Accept | 9 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 6.aggregate.confusion.Reject.Reject | 16 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 6.aggregate.count | 50 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 6.aggregate.macro_f1 | 0.5785 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 6.aggregate.per_label.Accept.f1 | 0.5532 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 6.aggregate.per_label.Accept.precision | 0.5909 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 6.aggregate.per_label.Accept.recall | 0.52 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 6.aggregate.per_label.Accept.support | 25 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 6.aggregate.per_label.Reject.f1 | 0.6038 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 6.aggregate.per_label.Reject.precision | 0.5714 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 6.aggregate.per_label.Reject.recall | 0.64 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 6.aggregate.per_label.Reject.support | 25 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 6.aggregate.roc_auc | 0.6496 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 6.feature_count | 27 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 6.fold_macro_f1_mean | 0.5625 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | 6.fold_macro_f1_std | 0.1435 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.4118 | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.4256 | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.4364 | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.437 | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.4459 | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.4513 | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.4636 | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.4728 | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.4839 | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.4963 | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.4996 | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.5 | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.5 | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.5 | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.5 | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.5 | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.5 | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.5 | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.5 | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.5 | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.515 | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.5164 | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.5201 | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.5203 | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.538 | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.5482 | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.5763 | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.6051 | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.629 | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | fold_at_0.6469 | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4118.accuracy | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4118.confusion.Accept.Accept | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4118.confusion.Accept.Reject | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4118.confusion.Reject.Accept | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4118.confusion.Reject.Reject | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4118.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4118.macro_f1 | 0.5833 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4118.per_label.Accept.f1 | 0.6667 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4118.per_label.Accept.precision | 0.5714 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4118.per_label.Accept.recall | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4118.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4118.per_label.Reject.f1 | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4118.per_label.Reject.precision | 0.6667 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4118.per_label.Reject.recall | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4118.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4118.roc_auc | 0.48 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4256.accuracy | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4256.confusion.Accept.Accept | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4256.confusion.Accept.Reject | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4256.confusion.Reject.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4256.confusion.Reject.Reject | 0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4256.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4256.macro_f1 | 0.2857 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4256.per_label.Accept.f1 | 0.5714 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4256.per_label.Accept.precision | 0.4444 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4256.per_label.Accept.recall | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4256.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4256.per_label.Reject.f1 | 0.0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4256.per_label.Reject.precision | 0.0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4256.per_label.Reject.recall | 0.0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4256.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4256.roc_auc | 0.32 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4364.accuracy | 0.9 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4364.confusion.Accept.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4364.confusion.Accept.Reject | 0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4364.confusion.Reject.Accept | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4364.confusion.Reject.Reject | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4364.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4364.macro_f1 | 0.899 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4364.per_label.Accept.f1 | 0.9091 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4364.per_label.Accept.precision | 0.8333 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4364.per_label.Accept.recall | 1.0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4364.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4364.per_label.Reject.f1 | 0.8889 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4364.per_label.Reject.precision | 1.0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4364.per_label.Reject.recall | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4364.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4364.roc_auc | 0.88 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.437.accuracy | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.437.confusion.Accept.Accept | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.437.confusion.Accept.Reject | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.437.confusion.Reject.Accept | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.437.confusion.Reject.Reject | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.437.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.437.macro_f1 | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.437.per_label.Accept.f1 | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.437.per_label.Accept.precision | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.437.per_label.Accept.recall | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.437.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.437.per_label.Reject.f1 | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.437.per_label.Reject.precision | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.437.per_label.Reject.recall | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.437.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.437.roc_auc | 0.84 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4459.accuracy | 0.7 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4459.confusion.Accept.Accept | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4459.confusion.Accept.Reject | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4459.confusion.Reject.Accept | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4459.confusion.Reject.Reject | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4459.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4459.macro_f1 | 0.697 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4459.per_label.Accept.f1 | 0.7273 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4459.per_label.Accept.precision | 0.6667 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4459.per_label.Accept.recall | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4459.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4459.per_label.Reject.f1 | 0.6667 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4459.per_label.Reject.precision | 0.75 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4459.per_label.Reject.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4459.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4459.roc_auc | 0.56 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4513.accuracy | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4513.confusion.Accept.Accept | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4513.confusion.Accept.Reject | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4513.confusion.Reject.Accept | 0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4513.confusion.Reject.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4513.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4513.macro_f1 | 0.7917 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4513.per_label.Accept.f1 | 0.75 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4513.per_label.Accept.precision | 1.0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4513.per_label.Accept.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4513.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4513.per_label.Reject.f1 | 0.8333 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4513.per_label.Reject.precision | 0.7143 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4513.per_label.Reject.recall | 1.0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4513.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4513.roc_auc | 1.0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4636.accuracy | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4636.confusion.Accept.Accept | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4636.confusion.Accept.Reject | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4636.confusion.Reject.Accept | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4636.confusion.Reject.Reject | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4636.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4636.macro_f1 | 0.4505 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4636.per_label.Accept.f1 | 0.2857 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4636.per_label.Accept.precision | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4636.per_label.Accept.recall | 0.2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4636.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4636.per_label.Reject.f1 | 0.6154 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4636.per_label.Reject.precision | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4636.per_label.Reject.recall | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4636.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4636.roc_auc | 0.76 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4728.accuracy | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4728.confusion.Accept.Accept | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4728.confusion.Accept.Reject | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4728.confusion.Reject.Accept | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4728.confusion.Reject.Reject | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4728.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4728.macro_f1 | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4728.per_label.Accept.f1 | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4728.per_label.Accept.precision | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4728.per_label.Accept.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4728.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4728.per_label.Reject.f1 | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4728.per_label.Reject.precision | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4728.per_label.Reject.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4728.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4728.roc_auc | 0.68 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4839.accuracy | 0.7 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4839.confusion.Accept.Accept | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4839.confusion.Accept.Reject | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4839.confusion.Reject.Accept | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4839.confusion.Reject.Reject | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4839.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4839.macro_f1 | 0.697 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4839.per_label.Accept.f1 | 0.7273 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4839.per_label.Accept.precision | 0.6667 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4839.per_label.Accept.recall | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4839.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4839.per_label.Reject.f1 | 0.6667 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4839.per_label.Reject.precision | 0.75 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4839.per_label.Reject.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4839.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4839.roc_auc | 0.72 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4963.accuracy | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4963.confusion.Accept.Accept | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4963.confusion.Accept.Reject | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4963.confusion.Reject.Accept | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4963.confusion.Reject.Reject | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4963.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4963.macro_f1 | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4963.per_label.Accept.f1 | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4963.per_label.Accept.precision | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4963.per_label.Accept.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4963.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4963.per_label.Reject.f1 | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4963.per_label.Reject.precision | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4963.per_label.Reject.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4963.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4963.roc_auc | 0.68 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4996.accuracy | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4996.confusion.Accept.Accept | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4996.confusion.Accept.Reject | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4996.confusion.Reject.Accept | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4996.confusion.Reject.Reject | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4996.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4996.macro_f1 | 0.375 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4996.per_label.Accept.f1 | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4996.per_label.Accept.precision | 0.4286 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4996.per_label.Accept.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4996.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4996.per_label.Reject.f1 | 0.25 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4996.per_label.Reject.precision | 0.3333 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4996.per_label.Reject.recall | 0.2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4996.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.4996.roc_auc | 0.32 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.accuracy | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.accuracy | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.accuracy | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.accuracy | 0.7 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.accuracy | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.accuracy | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.accuracy | 0.7 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.accuracy | 0.7 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.accuracy | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Accept.Accept | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Accept.Accept | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Accept.Accept | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Accept.Accept | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Accept.Accept | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Accept.Accept | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Accept.Accept | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Accept.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Accept.Accept | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Accept.Reject | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Accept.Reject | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Accept.Reject | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Accept.Reject | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Accept.Reject | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Accept.Reject | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Accept.Reject | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Accept.Reject | 0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Accept.Reject | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Reject.Accept | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Reject.Accept | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Reject.Accept | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Reject.Accept | 0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Reject.Accept | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Reject.Accept | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Reject.Accept | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Reject.Accept | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Reject.Accept | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Reject.Reject | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Reject.Reject | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Reject.Reject | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Reject.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Reject.Reject | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Reject.Reject | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Reject.Reject | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Reject.Reject | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.confusion.Reject.Reject | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.macro_f1 | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.macro_f1 | 0.5833 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.macro_f1 | 0.4949 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.macro_f1 | 0.6703 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.macro_f1 | 0.4949 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.macro_f1 | 0.4949 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.macro_f1 | 0.697 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.macro_f1 | 0.6703 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.macro_f1 | 0.375 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.f1 | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.f1 | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.f1 | 0.5455 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.f1 | 0.5714 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.f1 | 0.5455 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.f1 | 0.4444 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.f1 | 0.6667 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.f1 | 0.7692 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.f1 | 0.25 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.precision | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.precision | 0.6667 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.precision | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.precision | 1.0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.precision | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.precision | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.precision | 0.75 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.precision | 0.625 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.precision | 0.3333 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.recall | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.recall | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.recall | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.recall | 1.0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.recall | 0.2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.f1 | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.f1 | 0.6667 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.f1 | 0.4444 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.f1 | 0.7692 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.f1 | 0.4444 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.f1 | 0.5455 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.f1 | 0.7273 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.f1 | 0.5714 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.f1 | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.precision | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.precision | 0.5714 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.precision | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.precision | 0.625 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.precision | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.precision | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.precision | 0.6667 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.precision | 1.0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.precision | 0.4286 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.recall | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.recall | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.recall | 1.0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.recall | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.recall | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.recall | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.roc_auc | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.roc_auc | 0.76 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.roc_auc | 0.52 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.roc_auc | 0.92 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.roc_auc | 0.64 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.roc_auc | 0.72 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.roc_auc | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.roc_auc | 0.48 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5.roc_auc | 0.64 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.515.accuracy | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.515.confusion.Accept.Accept | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.515.confusion.Accept.Reject | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.515.confusion.Reject.Accept | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.515.confusion.Reject.Reject | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.515.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.515.macro_f1 | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.515.per_label.Accept.f1 | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.515.per_label.Accept.precision | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.515.per_label.Accept.recall | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.515.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.515.per_label.Reject.f1 | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.515.per_label.Reject.precision | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.515.per_label.Reject.recall | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.515.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.515.roc_auc | 0.88 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5164.accuracy | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5164.confusion.Accept.Accept | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5164.confusion.Accept.Reject | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5164.confusion.Reject.Accept | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5164.confusion.Reject.Reject | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5164.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5164.macro_f1 | 0.4505 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5164.per_label.Accept.f1 | 0.2857 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5164.per_label.Accept.precision | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5164.per_label.Accept.recall | 0.2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5164.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5164.per_label.Reject.f1 | 0.6154 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5164.per_label.Reject.precision | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5164.per_label.Reject.recall | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5164.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5164.roc_auc | 0.52 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5201.accuracy | 0.3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5201.confusion.Accept.Accept | 0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5201.confusion.Accept.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5201.confusion.Reject.Accept | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5201.confusion.Reject.Reject | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5201.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5201.macro_f1 | 0.2308 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5201.per_label.Accept.f1 | 0.0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5201.per_label.Accept.precision | 0.0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5201.per_label.Accept.recall | 0.0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5201.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5201.per_label.Reject.f1 | 0.4615 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5201.per_label.Reject.precision | 0.375 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5201.per_label.Reject.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5201.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5201.roc_auc | 0.32 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5203.accuracy | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5203.confusion.Accept.Accept | 0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5203.confusion.Accept.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5203.confusion.Reject.Accept | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5203.confusion.Reject.Reject | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5203.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5203.macro_f1 | 0.2857 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5203.per_label.Accept.f1 | 0.0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5203.per_label.Accept.precision | 0.0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5203.per_label.Accept.recall | 0.0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5203.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5203.per_label.Reject.f1 | 0.5714 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5203.per_label.Reject.precision | 0.4444 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5203.per_label.Reject.recall | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5203.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5203.roc_auc | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.538.accuracy | 0.7 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.538.confusion.Accept.Accept | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.538.confusion.Accept.Reject | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.538.confusion.Reject.Accept | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.538.confusion.Reject.Reject | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.538.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.538.macro_f1 | 0.697 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.538.per_label.Accept.f1 | 0.6667 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.538.per_label.Accept.precision | 0.75 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.538.per_label.Accept.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.538.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.538.per_label.Reject.f1 | 0.7273 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.538.per_label.Reject.precision | 0.6667 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.538.per_label.Reject.recall | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.538.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.538.roc_auc | 0.68 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5482.accuracy | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5482.confusion.Accept.Accept | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5482.confusion.Accept.Reject | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5482.confusion.Reject.Accept | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5482.confusion.Reject.Reject | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5482.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5482.macro_f1 | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5482.per_label.Accept.f1 | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5482.per_label.Accept.precision | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5482.per_label.Accept.recall | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5482.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5482.per_label.Reject.f1 | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5482.per_label.Reject.precision | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5482.per_label.Reject.recall | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5482.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5482.roc_auc | 0.28 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5763.accuracy | 0.7 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5763.confusion.Accept.Accept | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5763.confusion.Accept.Reject | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5763.confusion.Reject.Accept | 0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5763.confusion.Reject.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5763.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5763.macro_f1 | 0.6703 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5763.per_label.Accept.f1 | 0.5714 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5763.per_label.Accept.precision | 1.0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5763.per_label.Accept.recall | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5763.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5763.per_label.Reject.f1 | 0.7692 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5763.per_label.Reject.precision | 0.625 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5763.per_label.Reject.recall | 1.0 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5763.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.5763.roc_auc | 0.84 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6051.accuracy | 0.7 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6051.confusion.Accept.Accept | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6051.confusion.Accept.Reject | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6051.confusion.Reject.Accept | 1 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6051.confusion.Reject.Reject | 4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6051.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6051.macro_f1 | 0.697 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6051.per_label.Accept.f1 | 0.6667 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6051.per_label.Accept.precision | 0.75 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6051.per_label.Accept.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6051.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6051.per_label.Reject.f1 | 0.7273 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6051.per_label.Reject.precision | 0.6667 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6051.per_label.Reject.recall | 0.8 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6051.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6051.roc_auc | 0.88 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.629.accuracy | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.629.confusion.Accept.Accept | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.629.confusion.Accept.Reject | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.629.confusion.Reject.Accept | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.629.confusion.Reject.Reject | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.629.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.629.macro_f1 | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.629.per_label.Accept.f1 | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.629.per_label.Accept.precision | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.629.per_label.Accept.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.629.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.629.per_label.Reject.f1 | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.629.per_label.Reject.precision | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.629.per_label.Reject.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.629.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.629.roc_auc | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6469.accuracy | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6469.confusion.Accept.Accept | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6469.confusion.Accept.Reject | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6469.confusion.Reject.Accept | 3 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6469.confusion.Reject.Reject | 2 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6469.count | 10 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6469.macro_f1 | 0.4949 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6469.per_label.Accept.f1 | 0.5455 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6469.per_label.Accept.precision | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6469.per_label.Accept.recall | 0.6 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6469.per_label.Accept.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6469.per_label.Reject.f1 | 0.4444 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6469.per_label.Reject.precision | 0.5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6469.per_label.Reject.recall | 0.4 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6469.per_label.Reject.support | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | metrics_at_0.6469.roc_auc | 0.36 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.4118.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.4118.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.4256.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.4256.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.4364.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.4364.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.437.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.437.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.4459.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.4459.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.4513.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.4513.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.4636.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.4636.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.4728.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.4728.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.4839.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.4839.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.4963.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.4963.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.4996.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.4996.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.515.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.515.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5164.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5164.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5201.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5201.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5203.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5203.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.538.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.538.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5482.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5482.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5763.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.5763.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.6051.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.6051.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.629.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.629.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.6469.Accept | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | classification | auxiliary_classifier | aggregate | test_label_counts_at_0.6469.Reject | 5 | diagnostic | local_decision_classifier_metrics.json |
| Local OpenReview/PRISM | generation | glm_reviewer | aggregate | covered_human_weakness_count_at_0.12 | 239 | diagnostic | glm_reviewer_coverage_metrics.json |
| Local OpenReview/PRISM | generation | glm_reviewer | aggregate | covered_human_weakness_count_at_0.18 | 172 | diagnostic | glm_reviewer_coverage_metrics.json |
| Local OpenReview/PRISM | generation | glm_reviewer | aggregate | covered_human_weakness_count_at_0.24 | 39 | diagnostic | glm_reviewer_coverage_metrics.json |
| Local OpenReview/PRISM | generation | glm_reviewer | aggregate | evaluated_human_weakness_count_at_0.12 | 289 | diagnostic | glm_reviewer_coverage_metrics.json |
| Local OpenReview/PRISM | generation | glm_reviewer | aggregate | evaluated_human_weakness_count_at_0.18 | 289 | diagnostic | glm_reviewer_coverage_metrics.json |
| Local OpenReview/PRISM | generation | glm_reviewer | aggregate | evaluated_human_weakness_count_at_0.24 | 289 | diagnostic | glm_reviewer_coverage_metrics.json |
| Local OpenReview/PRISM | generation | glm_reviewer | aggregate | generic_rate | 0.0741 | diagnostic | glm_reviewer_coverage_metrics.json |
| Local OpenReview/PRISM | generation | glm_reviewer | aggregate | human_weakness_recall_at_0.12 | 0.827 | diagnostic | glm_reviewer_coverage_metrics.json |
| Local OpenReview/PRISM | generation | glm_reviewer | aggregate | human_weakness_recall_at_0.18 | 0.5952 | diagnostic | glm_reviewer_coverage_metrics.json |
| Local OpenReview/PRISM | generation | glm_reviewer | aggregate | human_weakness_recall_at_0.24 | 0.1349 | diagnostic | glm_reviewer_coverage_metrics.json |
| Local OpenReview/PRISM | generation | minimax_reviewer | aggregate | covered_human_weakness_count_at_0.12 | 130 | diagnostic | minimax_reviewer_coverage_metrics.json |
| Local OpenReview/PRISM | generation | minimax_reviewer | aggregate | covered_human_weakness_count_at_0.18 | 79 | diagnostic | minimax_reviewer_coverage_metrics.json |
| Local OpenReview/PRISM | generation | minimax_reviewer | aggregate | covered_human_weakness_count_at_0.24 | 24 | diagnostic | minimax_reviewer_coverage_metrics.json |
| Local OpenReview/PRISM | generation | minimax_reviewer | aggregate | evaluated_human_weakness_count_at_0.12 | 151 | diagnostic | minimax_reviewer_coverage_metrics.json |
| Local OpenReview/PRISM | generation | minimax_reviewer | aggregate | evaluated_human_weakness_count_at_0.18 | 151 | diagnostic | minimax_reviewer_coverage_metrics.json |
| Local OpenReview/PRISM | generation | minimax_reviewer | aggregate | evaluated_human_weakness_count_at_0.24 | 151 | diagnostic | minimax_reviewer_coverage_metrics.json |
| Local OpenReview/PRISM | generation | minimax_reviewer | aggregate | generic_rate | 0.0667 | diagnostic | minimax_reviewer_coverage_metrics.json |
| Local OpenReview/PRISM | generation | minimax_reviewer | aggregate | human_weakness_recall_at_0.12 | 0.8609 | diagnostic | minimax_reviewer_coverage_metrics.json |
| Local OpenReview/PRISM | generation | minimax_reviewer | aggregate | human_weakness_recall_at_0.18 | 0.5232 | diagnostic | minimax_reviewer_coverage_metrics.json |
| Local OpenReview/PRISM | generation | minimax_reviewer | aggregate | human_weakness_recall_at_0.24 | 0.1589 | diagnostic | minimax_reviewer_coverage_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | category_counts.clarity | 2 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | category_counts.experiment | 5 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | category_counts.method | 1 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | category_counts.reproducibility | 1 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | category_counts.validity | 3 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | covered_human_weakness_count_at_0.12 | 118 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | covered_human_weakness_count_at_0.18 | 79 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | covered_human_weakness_count_at_0.24 | 19 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | generated_weakness_count | 12 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | generic_rate | 0.0833 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | human_weakness_count | 151 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | human_weakness_count_at_0.12 | 151 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | human_weakness_count_at_0.18 | 151 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | human_weakness_count_at_0.24 | 151 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | human_weakness_recall_at_0.12 | 0.7815 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | human_weakness_recall_at_0.18 | 0.5232 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | human_weakness_recall_at_0.24 | 0.1258 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | mean_generated_per_paper | 2.4 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | mean_paper_recall_at_0.12 | 0.8098 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | mean_paper_recall_at_0.18 | 0.53 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | mean_paper_recall_at_0.24 | 0.125 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | paper_count | 5 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | redundancy_rate | 0.0 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | severity_counts.major | 9 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | severity_counts.minor | 3 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | support.label_counts.Mentioned but Not Problem | 6 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | support.label_counts.Partially Supported | 4 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | support.label_counts.Unsupported | 2 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | support.mean_support_score | 0.3751 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | support.partially_supported_or_better_rate | 0.3333 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | glm_reviewer | support.verified_count | 12 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | category_counts.experiment | 7 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | category_counts.method | 3 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | category_counts.related_work | 1 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | category_counts.reproducibility | 3 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | category_counts.validity | 1 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | covered_human_weakness_count_at_0.12 | 130 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | covered_human_weakness_count_at_0.18 | 79 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | covered_human_weakness_count_at_0.24 | 24 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | generated_weakness_count | 15 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | generic_rate | 0.0667 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | human_weakness_count | 151 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | human_weakness_count_at_0.12 | 151 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | human_weakness_count_at_0.18 | 151 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | human_weakness_count_at_0.24 | 151 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | human_weakness_recall_at_0.12 | 0.8609 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | human_weakness_recall_at_0.18 | 0.5232 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | human_weakness_recall_at_0.24 | 0.1589 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | mean_generated_per_paper | 3.0 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | mean_paper_recall_at_0.12 | 0.8684 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | mean_paper_recall_at_0.18 | 0.5421 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | mean_paper_recall_at_0.24 | 0.1686 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | paper_count | 5 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | redundancy_rate | 0.0 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | severity_counts.major | 9 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | severity_counts.minor | 6 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | support.label_counts.Mentioned but Not Problem | 7 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | support.label_counts.Partially Supported | 5 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | support.label_counts.Supported | 2 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | support.label_counts.Unsupported | 1 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | support.mean_support_score | 0.467 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | support.partially_supported_or_better_rate | 0.4667 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | minimax_reviewer | support.verified_count | 15 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | category_counts.experiment | 6 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | category_counts.limitation | 5 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | category_counts.method | 5 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | category_counts.related_work | 3 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | category_counts.reproducibility | 1 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | covered_human_weakness_count_at_0.12 | 120 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | covered_human_weakness_count_at_0.18 | 67 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | covered_human_weakness_count_at_0.24 | 14 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | generated_weakness_count | 20 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | generic_rate | 0.15 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | human_weakness_count | 151 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | human_weakness_count_at_0.12 | 151 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | human_weakness_count_at_0.18 | 151 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | human_weakness_count_at_0.24 | 151 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | human_weakness_recall_at_0.12 | 0.7947 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | human_weakness_recall_at_0.18 | 0.4437 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | human_weakness_recall_at_0.24 | 0.0927 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | mean_generated_per_paper | 4.0 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | mean_paper_recall_at_0.12 | 0.8288 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | mean_paper_recall_at_0.18 | 0.4483 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | mean_paper_recall_at_0.24 | 0.0985 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | paper_count | 5 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | redundancy_rate | 0.1316 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | severity_counts.major | 14 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | severity_counts.minor | 6 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | support.label_counts.Mentioned but Not Problem | 10 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | support.label_counts.Unsupported | 10 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | support.mean_support_score | 0.2061 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | support.partially_supported_or_better_rate | 0.0 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | reviewer_comparison | rubric_agent | support.verified_count | 20 | diagnostic | generated_reviewer_comparison_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | category_recall_at_0.12.clarity | 0.8837 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | category_recall_at_0.12.experiment | 0.8918 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | category_recall_at_0.12.method | 0.8382 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | category_recall_at_0.12.other | 0.7136 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | category_recall_at_0.12.related_work | 0.9457 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | category_recall_at_0.12.reproducibility | 0.6111 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | category_recall_at_0.12.validity | 0.875 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | category_recall_at_0.18.clarity | 0.4186 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | category_recall_at_0.18.experiment | 0.5718 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | category_recall_at_0.18.method | 0.496 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | category_recall_at_0.18.other | 0.3065 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | category_recall_at_0.18.related_work | 0.7752 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | category_recall_at_0.18.reproducibility | 0.1667 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | category_recall_at_0.18.validity | 0.625 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | category_recall_at_0.24.clarity | 0.093 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | category_recall_at_0.24.experiment | 0.0918 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | category_recall_at_0.24.method | 0.0796 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | category_recall_at_0.24.other | 0.0291 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | category_recall_at_0.24.related_work | 0.2481 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | category_recall_at_0.24.reproducibility | 0.0556 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | category_recall_at_0.24.validity | 0.125 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | covered_human_weakness_count_at_0.12 | 1206 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | covered_human_weakness_count_at_0.18 | 703 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | covered_human_weakness_count_at_0.24 | 122 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | generated_category_counts.experiment | 55 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | generated_category_counts.limitation | 36 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | generated_category_counts.method | 56 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | generated_category_counts.related_work | 35 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | generated_category_counts.reproducibility | 12 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | generated_severity_counts.major | 146 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | generated_severity_counts.minor | 48 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | generated_weakness_count | 194 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | generic_rate | 0.1804 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | human_weakness_count | 1463 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | human_weakness_count_at_0.12 | 1463 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | human_weakness_count_at_0.18 | 1463 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | human_weakness_count_at_0.24 | 1463 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | human_weakness_recall_at_0.12 | 0.8243 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | human_weakness_recall_at_0.18 | 0.4805 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | human_weakness_recall_at_0.24 | 0.0834 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | mean_generated_per_paper | 3.88 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | mean_paper_recall_at_0.12 | 0.8331 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | mean_paper_recall_at_0.18 | 0.4798 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | mean_paper_recall_at_0.24 | 0.0844 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | paper_count | 50 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | redundancy_rate | 0.1531 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | top_match_examples.0.similarity | 0.3393 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | top_match_examples.1.similarity | 0.3238 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | top_match_examples.2.similarity | 0.3234 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | top_match_examples.3.similarity | 0.3079 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | top_match_examples.4.similarity | 0.3071 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | top_match_examples.5.similarity | 0.3029 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | top_match_examples.6.similarity | 0.2925 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | generation | rubric_agent | aggregate | top_match_examples.7.similarity | 0.2922 | proxy | rubric_agent_coverage_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | glm_reviewer | candidate_count | 27 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | glm_reviewer | candidate_label_counts.Mentioned but Not Problem | 7 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | glm_reviewer | candidate_label_counts.Partially Supported | 14 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | glm_reviewer | candidate_label_counts.Supported | 4 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | glm_reviewer | candidate_label_counts.Unsupported | 2 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | glm_reviewer | candidate_mean_support | 0.5212 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | glm_reviewer | candidate_partially_supported_or_better_rate | 0.6667 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | glm_reviewer | paper_count | 10 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | glm_reviewer | top3_category_counts.clarity | 5 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | glm_reviewer | top3_category_counts.experiment | 13 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | glm_reviewer | top3_category_counts.method | 3 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | glm_reviewer | top3_category_counts.reproducibility | 3 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | glm_reviewer | top3_category_counts.validity | 3 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | glm_reviewer | top3_count | 27 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | glm_reviewer | top3_label_counts.Mentioned but Not Problem | 7 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | glm_reviewer | top3_label_counts.Partially Supported | 14 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | glm_reviewer | top3_label_counts.Supported | 4 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | glm_reviewer | top3_label_counts.Unsupported | 2 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | glm_reviewer | top3_mean_support | 0.5212 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | glm_reviewer | top3_partially_supported_or_better_rate | 0.6667 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | rubric_agent | candidate_count | 194 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | rubric_agent | candidate_label_counts.Mentioned but Not Problem | 76 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | rubric_agent | candidate_label_counts.Partially Supported | 5 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | rubric_agent | candidate_label_counts.Unsupported | 113 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | rubric_agent | candidate_mean_support | 0.1999 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | rubric_agent | candidate_partially_supported_or_better_rate | 0.0258 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | rubric_agent | paper_count | 49 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | rubric_agent | top3_category_counts.experiment | 46 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | rubric_agent | top3_category_counts.limitation | 17 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | rubric_agent | top3_category_counts.method | 51 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | rubric_agent | top3_category_counts.related_work | 22 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | rubric_agent | top3_category_counts.reproducibility | 5 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | rubric_agent | top3_count | 141 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | rubric_agent | top3_label_counts.Mentioned but Not Problem | 72 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | rubric_agent | top3_label_counts.Partially Supported | 5 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | rubric_agent | top3_label_counts.Unsupported | 64 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | rubric_agent | top3_mean_support | 0.2343 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | ranker | generated_weakness_ranker | rubric_agent | top3_partially_supported_or_better_rate | 0.0355 | diagnostic | generated_weakness_ranker_metrics.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | glm_reviewer | generated_weakness_count | 27 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | glm_reviewer | label_counts.Mentioned but Not Problem | 7 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | glm_reviewer | label_counts.Partially Supported | 14 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | glm_reviewer | label_counts.Supported | 4 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | glm_reviewer | label_counts.Unsupported | 2 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | glm_reviewer | mean_support_score | 0.5212 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | glm_reviewer | non_empty_retrieval_count | 27 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | glm_reviewer | partially_supported_or_better_rate | 0.6667 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | glm_reviewer | top1_section_alignment_rate | 1.0 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | glm_reviewer | top1_tool_mix.keyword_search | 8 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | glm_reviewer | top1_tool_mix.section_read | 1 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | glm_reviewer | top1_tool_mix.semantic_search | 18 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | glm_reviewer | top3_section_alignment_rate | 1.0 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | rubric_agent | generated_weakness_count | 194 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | rubric_agent | label_counts.Mentioned but Not Problem | 76 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | rubric_agent | label_counts.Partially Supported | 5 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | rubric_agent | label_counts.Unsupported | 113 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | rubric_agent | mean_support_score | 0.1999 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | rubric_agent | non_empty_retrieval_count | 194 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | rubric_agent | partially_supported_or_better_rate | 0.0258 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | rubric_agent | top1_section_alignment_rate | 1.0 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | rubric_agent | top1_tool_mix.keyword_search | 72 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | rubric_agent | top1_tool_mix.section_read | 7 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | rubric_agent | top1_tool_mix.semantic_search | 115 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | generated_weakness_rag | rubric_agent | top3_section_alignment_rate | 1.0 | diagnostic | generated_hierarchical_retrieval_summary.json |
| Local OpenReview/PRISM | retrieval | paper_rag | bm25 | avg_top1_score | 24.839129 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | bm25 | avg_top5_score | 19.684136 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | bm25 | avg_topk_section_diversity | 2.6503 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | bm25 | non_empty_count | 1447 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | bm25 | non_empty_rate | 0.9891 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | bm25 | query_count | 1463 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | bm25 | top1_section_alignment_rate | 0.6151 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | bm25 | top1_section_counts.abstract | 68 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | bm25 | top1_section_counts.conclusion | 21 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | bm25 | top1_section_counts.experiment | 218 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | bm25 | top1_section_counts.introduction | 203 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | bm25 | top1_section_counts.limitation | 57 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | bm25 | top1_section_counts.method | 469 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | bm25 | top1_section_counts.other | 268 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | bm25 | top1_section_counts.reference | 33 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | bm25 | top1_section_counts.related_work | 110 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | bm25 | top3_any_section_alignment_rate | 0.8341 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | human_hierarchical_paper_rag | avg_top1_score | 0.246929 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | human_hierarchical_paper_rag | avg_top5_score | 0.230234 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | human_hierarchical_paper_rag | avg_topk_section_diversity | 1.864 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | human_hierarchical_paper_rag | non_empty_count | 1463 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | human_hierarchical_paper_rag | non_empty_rate | 1.0 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | human_hierarchical_paper_rag | query_count | 1463 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | human_hierarchical_paper_rag | top1_section_alignment_rate | 0.9993 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | human_hierarchical_paper_rag | top1_section_counts.abstract | 59 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | human_hierarchical_paper_rag | top1_section_counts.experiment | 431 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | human_hierarchical_paper_rag | top1_section_counts.introduction | 156 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | human_hierarchical_paper_rag | top1_section_counts.limitation | 25 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | human_hierarchical_paper_rag | top1_section_counts.method | 668 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | human_hierarchical_paper_rag | top1_section_counts.other | 80 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | human_hierarchical_paper_rag | top1_section_counts.reference | 1 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | human_hierarchical_paper_rag | top1_section_counts.related_work | 43 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | human_hierarchical_paper_rag | top3_any_section_alignment_rate | 1.0 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | hybrid_bm25_tfidf | avg_top1_score | 0.88312 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | hybrid_bm25_tfidf | avg_top5_score | 0.641539 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | hybrid_bm25_tfidf | avg_topk_section_diversity | 2.6455 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | hybrid_bm25_tfidf | non_empty_count | 1447 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | hybrid_bm25_tfidf | non_empty_rate | 0.9891 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | hybrid_bm25_tfidf | query_count | 1463 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | hybrid_bm25_tfidf | top1_section_alignment_rate | 0.6164 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | hybrid_bm25_tfidf | top1_section_counts.abstract | 79 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | hybrid_bm25_tfidf | top1_section_counts.conclusion | 24 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | hybrid_bm25_tfidf | top1_section_counts.experiment | 201 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | hybrid_bm25_tfidf | top1_section_counts.introduction | 180 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | hybrid_bm25_tfidf | top1_section_counts.limitation | 54 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | hybrid_bm25_tfidf | top1_section_counts.method | 486 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | hybrid_bm25_tfidf | top1_section_counts.other | 293 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | hybrid_bm25_tfidf | top1_section_counts.reference | 24 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | hybrid_bm25_tfidf | top1_section_counts.related_work | 106 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | hybrid_bm25_tfidf | top3_any_section_alignment_rate | 0.83 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | section_aware_hybrid | avg_top1_score | 0.949624 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | section_aware_hybrid | avg_top5_score | 0.702738 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | section_aware_hybrid | avg_topk_section_diversity | 2.6192 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | section_aware_hybrid | non_empty_count | 1447 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | section_aware_hybrid | non_empty_rate | 0.9891 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | section_aware_hybrid | query_count | 1463 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | section_aware_hybrid | top1_section_alignment_rate | 0.7021 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | section_aware_hybrid | top1_section_counts.abstract | 70 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | section_aware_hybrid | top1_section_counts.conclusion | 17 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | section_aware_hybrid | top1_section_counts.experiment | 242 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | section_aware_hybrid | top1_section_counts.introduction | 159 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | section_aware_hybrid | top1_section_counts.limitation | 51 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | section_aware_hybrid | top1_section_counts.method | 538 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | section_aware_hybrid | top1_section_counts.other | 265 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | section_aware_hybrid | top1_section_counts.reference | 24 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | section_aware_hybrid | top1_section_counts.related_work | 81 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | section_aware_hybrid | top3_any_section_alignment_rate | 0.8618 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | tfidf_cosine | avg_top1_score | 0.153045 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | tfidf_cosine | avg_top5_score | 0.118996 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | tfidf_cosine | avg_topk_section_diversity | 2.5847 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | tfidf_cosine | non_empty_count | 1447 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | tfidf_cosine | non_empty_rate | 0.9891 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | tfidf_cosine | query_count | 1463 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | tfidf_cosine | top1_section_alignment_rate | 0.6247 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | tfidf_cosine | top1_section_counts.abstract | 81 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | tfidf_cosine | top1_section_counts.conclusion | 38 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | tfidf_cosine | top1_section_counts.experiment | 183 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | tfidf_cosine | top1_section_counts.introduction | 141 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | tfidf_cosine | top1_section_counts.limitation | 49 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | tfidf_cosine | top1_section_counts.method | 515 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | tfidf_cosine | top1_section_counts.other | 324 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | tfidf_cosine | top1_section_counts.reference | 23 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | tfidf_cosine | top1_section_counts.related_work | 93 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | retrieval | paper_rag | tfidf_cosine | top3_any_section_alignment_rate | 0.8238 | proxy | retrieval_proxy_eval.json |
| Local OpenReview/PRISM | verification | glm_reviewer | aggregate | label_counts.Mentioned but Not Problem | 9 | silver | glm_reviewer_verifier_summary.json |
| Local OpenReview/PRISM | verification | glm_reviewer | aggregate | label_counts.Partially Supported | 13 | silver | glm_reviewer_verifier_summary.json |
| Local OpenReview/PRISM | verification | glm_reviewer | aggregate | label_counts.Supported | 2 | silver | glm_reviewer_verifier_summary.json |
| Local OpenReview/PRISM | verification | glm_reviewer | aggregate | label_counts.Unsupported | 3 | silver | glm_reviewer_verifier_summary.json |
| Local OpenReview/PRISM | verification | glm_reviewer | aggregate | mean_support_score | 0.467 | silver | glm_reviewer_verifier_summary.json |
| Local OpenReview/PRISM | verification | glm_reviewer | aggregate | retrieved_count | 27 | silver | glm_reviewer_verifier_summary.json |
| Local OpenReview/PRISM | verification | glm_reviewer | aggregate | verified_count | 27 | silver | glm_reviewer_verifier_summary.json |
| Local OpenReview/PRISM | verification | minimax_reviewer | aggregate | label_counts.Mentioned but Not Problem | 7 | silver | minimax_reviewer_verifier_summary.json |
| Local OpenReview/PRISM | verification | minimax_reviewer | aggregate | label_counts.Partially Supported | 5 | silver | minimax_reviewer_verifier_summary.json |
| Local OpenReview/PRISM | verification | minimax_reviewer | aggregate | label_counts.Supported | 2 | silver | minimax_reviewer_verifier_summary.json |
| Local OpenReview/PRISM | verification | minimax_reviewer | aggregate | label_counts.Unsupported | 1 | silver | minimax_reviewer_verifier_summary.json |
| Local OpenReview/PRISM | verification | minimax_reviewer | aggregate | mean_support_score | 0.467 | silver | minimax_reviewer_verifier_summary.json |
| Local OpenReview/PRISM | verification | minimax_reviewer | aggregate | retrieved_count | 15 | silver | minimax_reviewer_verifier_summary.json |
| Local OpenReview/PRISM | verification | minimax_reviewer | aggregate | verified_count | 15 | silver | minimax_reviewer_verifier_summary.json |
| Local OpenReview/PRISM | verification | rubric_agent | aggregate | category_counts.experiment | 55 | silver | rubric_agent_verifier_summary.json |
| Local OpenReview/PRISM | verification | rubric_agent | aggregate | category_counts.limitation | 36 | silver | rubric_agent_verifier_summary.json |
| Local OpenReview/PRISM | verification | rubric_agent | aggregate | category_counts.method | 56 | silver | rubric_agent_verifier_summary.json |
| Local OpenReview/PRISM | verification | rubric_agent | aggregate | category_counts.related_work | 35 | silver | rubric_agent_verifier_summary.json |
| Local OpenReview/PRISM | verification | rubric_agent | aggregate | category_counts.reproducibility | 12 | silver | rubric_agent_verifier_summary.json |
| Local OpenReview/PRISM | verification | rubric_agent | aggregate | generated_weakness_count | 194 | silver | rubric_agent_verifier_summary.json |
| Local OpenReview/PRISM | verification | rubric_agent | aggregate | label_counts.Mentioned but Not Problem | 70 | silver | rubric_agent_verifier_summary.json |
| Local OpenReview/PRISM | verification | rubric_agent | aggregate | label_counts.Partially Supported | 3 | silver | rubric_agent_verifier_summary.json |
| Local OpenReview/PRISM | verification | rubric_agent | aggregate | label_counts.Unsupported | 121 | silver | rubric_agent_verifier_summary.json |
| Local OpenReview/PRISM | verification | rubric_agent | aggregate | mean_rank_score | 0.1198 | silver | rubric_agent_verifier_summary.json |
| Local OpenReview/PRISM | verification | rubric_agent | aggregate | mean_support_score | 0.1867 | silver | rubric_agent_verifier_summary.json |
| Local OpenReview/PRISM | verification | rubric_agent | aggregate | paper_count | 49 | silver | rubric_agent_verifier_summary.json |
| Local OpenReview/PRISM | verification | rubric_agent | aggregate | severity_counts.major | 146 | silver | rubric_agent_verifier_summary.json |
| Local OpenReview/PRISM | verification | rubric_agent | aggregate | severity_counts.minor | 48 | silver | rubric_agent_verifier_summary.json |
| Local OpenReview/PRISM | verification | rubric_agent | aggregate | top3_count | 141 | silver | rubric_agent_verifier_summary.json |
| Local OpenReview/PRISM | verification | rubric_agent | aggregate | top3_label_counts.Mentioned but Not Problem | 68 | silver | rubric_agent_verifier_summary.json |
| Local OpenReview/PRISM | verification | rubric_agent | aggregate | top3_label_counts.Partially Supported | 3 | silver | rubric_agent_verifier_summary.json |
| Local OpenReview/PRISM | verification | rubric_agent | aggregate | top3_label_counts.Unsupported | 70 | silver | rubric_agent_verifier_summary.json |
| Local Version Drift Fixture | review_audit | agent_rag | manifest | run_count | 1 | silver | manifest:experiment-9f61e4b0fe4548f0b52692c67290a105 |
| Local Version Drift Fixture | review_audit | agent_rag | manifest | succeeded_rate | 1.0 | silver | manifest:experiment-9f61e4b0fe4548f0b52692c67290a105 |
| Local Version Drift Fixture | review_audit | agent_rag | manifest | succeeded_run_count | 1 | silver | manifest:experiment-9f61e4b0fe4548f0b52692c67290a105 |
| Local Version Drift Fixture | review_audit | generation | manifest | weakness_count | 1 | silver | manifest:experiment-9f61e4b0fe4548f0b52692c67290a105 |
| Local Version Drift Fixture | review_audit | ranking | manifest | ranked_finding_count | 1 | silver | manifest:experiment-9f61e4b0fe4548f0b52692c67290a105 |
| Local Version Drift Fixture | review_audit | verification | manifest | mean_support_score | 0.3333 | silver | manifest:experiment-9f61e4b0fe4548f0b52692c67290a105 |
| PeerQA-XT | retrieval | paper_rag | bm25_question | answer_support_hit_at_1 | 0.24 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | bm25_question | answer_support_hit_at_3 | 0.598 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | bm25_question | answer_support_hit_at_5 | 0.794 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | bm25_question | mean_answer_token_recall_at_1 | 0.2518 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | bm25_question | mean_answer_token_recall_at_3 | 0.4223 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | bm25_question | mean_answer_token_recall_at_5 | 0.5001 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | bm25_question | min_answer_recall_for_hit | 0.35 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | bm25_question | usable_rows | 500 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | domain_hierarchical_question | answer_support_hit_at_1 | 0.214 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | domain_hierarchical_question | answer_support_hit_at_3 | 0.526 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | domain_hierarchical_question | answer_support_hit_at_5 | 0.734 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | domain_hierarchical_question | mean_answer_token_recall_at_1 | 0.2307 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | domain_hierarchical_question | mean_answer_token_recall_at_3 | 0.391 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | domain_hierarchical_question | mean_answer_token_recall_at_5 | 0.4752 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | domain_hierarchical_question | min_answer_recall_for_hit | 0.35 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | domain_hierarchical_question | usable_rows | 500 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | domain_section_aware_question | answer_support_hit_at_1 | 0.208 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | domain_section_aware_question | answer_support_hit_at_3 | 0.536 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | domain_section_aware_question | answer_support_hit_at_5 | 0.742 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | domain_section_aware_question | mean_answer_token_recall_at_1 | 0.2323 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | domain_section_aware_question | mean_answer_token_recall_at_3 | 0.3951 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | domain_section_aware_question | mean_answer_token_recall_at_5 | 0.4774 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | domain_section_aware_question | min_answer_recall_for_hit | 0.35 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | domain_section_aware_question | usable_rows | 500 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | hierarchical_question | answer_support_hit_at_1 | 0.222 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | hierarchical_question | answer_support_hit_at_3 | 0.59 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | hierarchical_question | answer_support_hit_at_5 | 0.788 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | hierarchical_question | mean_answer_token_recall_at_1 | 0.2436 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | hierarchical_question | mean_answer_token_recall_at_3 | 0.4209 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | hierarchical_question | mean_answer_token_recall_at_5 | 0.4995 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | hierarchical_question | min_answer_recall_for_hit | 0.35 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | hierarchical_question | usable_rows | 500 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | hybrid_question | answer_support_hit_at_1 | 0.242 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | hybrid_question | answer_support_hit_at_3 | 0.596 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | hybrid_question | answer_support_hit_at_5 | 0.792 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | hybrid_question | mean_answer_token_recall_at_1 | 0.2521 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | hybrid_question | mean_answer_token_recall_at_3 | 0.4193 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | hybrid_question | mean_answer_token_recall_at_5 | 0.4988 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | hybrid_question | min_answer_recall_for_hit | 0.35 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | hybrid_question | usable_rows | 500 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | oracle_answer_query | answer_support_hit_at_1 | 0.496 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | oracle_answer_query | answer_support_hit_at_3 | 0.902 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | oracle_answer_query | answer_support_hit_at_5 | 0.966 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | oracle_answer_query | mean_answer_token_recall_at_1 | 0.3709 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | oracle_answer_query | mean_answer_token_recall_at_3 | 0.5547 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | oracle_answer_query | mean_answer_token_recall_at_5 | 0.6257 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | oracle_answer_query | min_answer_recall_for_hit | 0.35 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | oracle_answer_query | usable_rows | 500 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | prf_section_aware_question | answer_support_hit_at_1 | 0.244 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | prf_section_aware_question | answer_support_hit_at_3 | 0.582 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | prf_section_aware_question | answer_support_hit_at_5 | 0.78 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | prf_section_aware_question | mean_answer_token_recall_at_1 | 0.2522 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | prf_section_aware_question | mean_answer_token_recall_at_3 | 0.4188 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | prf_section_aware_question | mean_answer_token_recall_at_5 | 0.498 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | prf_section_aware_question | min_answer_recall_for_hit | 0.35 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | prf_section_aware_question | usable_rows | 500 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | query_decomposed_question | answer_support_hit_at_1 | 0.208 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | query_decomposed_question | answer_support_hit_at_3 | 0.532 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | query_decomposed_question | answer_support_hit_at_5 | 0.734 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | query_decomposed_question | mean_answer_token_recall_at_1 | 0.2335 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | query_decomposed_question | mean_answer_token_recall_at_3 | 0.3929 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | query_decomposed_question | mean_answer_token_recall_at_5 | 0.4751 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | query_decomposed_question | min_answer_recall_for_hit | 0.35 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | query_decomposed_question | usable_rows | 500 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | section_aware_question | answer_support_hit_at_1 | 0.246 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | section_aware_question | answer_support_hit_at_3 | 0.606 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | section_aware_question | answer_support_hit_at_5 | 0.806 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | section_aware_question | mean_answer_token_recall_at_1 | 0.2527 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | section_aware_question | mean_answer_token_recall_at_3 | 0.4234 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | section_aware_question | mean_answer_token_recall_at_5 | 0.5005 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | section_aware_question | min_answer_recall_for_hit | 0.35 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | section_aware_question | usable_rows | 500 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | tfidf_question | answer_support_hit_at_1 | 0.23 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | tfidf_question | answer_support_hit_at_3 | 0.592 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | tfidf_question | answer_support_hit_at_5 | 0.774 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | tfidf_question | mean_answer_token_recall_at_1 | 0.247 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | tfidf_question | mean_answer_token_recall_at_3 | 0.418 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | tfidf_question | mean_answer_token_recall_at_5 | 0.4906 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | tfidf_question | min_answer_recall_for_hit | 0.35 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerQA-XT | retrieval | paper_rag | tfidf_question | usable_rows | 500 | proxy | peerqa_xt_retrieval_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_context_multinomial_naive_bayes_v2.accuracy | 0.788 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_context_multinomial_naive_bayes_v2.confusion.Correct.Correct | 602 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_context_multinomial_naive_bayes_v2.confusion.Correct.Not Correct | 94 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_context_multinomial_naive_bayes_v2.confusion.Not Correct.Correct | 76 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_context_multinomial_naive_bayes_v2.confusion.Not Correct.Not Correct | 30 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_context_multinomial_naive_bayes_v2.count | 802 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_context_multinomial_naive_bayes_v2.label_counts.Correct | 696 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_context_multinomial_naive_bayes_v2.label_counts.Not Correct | 106 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_context_multinomial_naive_bayes_v2.macro_f1 | 0.5686 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Correct.f1 | 0.8763 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Correct.precision | 0.8879 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Correct.recall | 0.8649 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Correct.support | 696 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Not Correct.f1 | 0.2609 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Not Correct.precision | 0.2419 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Not Correct.recall | 0.283 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Not Correct.support | 106 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_context_multinomial_naive_bayes_v2.prediction_counts.Correct | 678 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_context_multinomial_naive_bayes_v2.prediction_counts.Not Correct | 124 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_multinomial_naive_bayes_v1.accuracy | 0.8242 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_multinomial_naive_bayes_v1.confusion.Correct.Correct | 656 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_multinomial_naive_bayes_v1.confusion.Correct.Not Correct | 40 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_multinomial_naive_bayes_v1.confusion.Not Correct.Correct | 101 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_multinomial_naive_bayes_v1.confusion.Not Correct.Not Correct | 5 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_multinomial_naive_bayes_v1.count | 802 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_multinomial_naive_bayes_v1.label_counts.Correct | 696 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_multinomial_naive_bayes_v1.label_counts.Not Correct | 106 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_multinomial_naive_bayes_v1.macro_f1 | 0.4846 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_multinomial_naive_bayes_v1.per_label.Correct.f1 | 0.903 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_multinomial_naive_bayes_v1.per_label.Correct.precision | 0.8666 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_multinomial_naive_bayes_v1.per_label.Correct.recall | 0.9425 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_multinomial_naive_bayes_v1.per_label.Correct.support | 696 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_multinomial_naive_bayes_v1.per_label.Not Correct.f1 | 0.0662 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_multinomial_naive_bayes_v1.per_label.Not Correct.precision | 0.1111 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_multinomial_naive_bayes_v1.per_label.Not Correct.recall | 0.0472 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_multinomial_naive_bayes_v1.per_label.Not Correct.support | 106 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_multinomial_naive_bayes_v1.prediction_counts.Correct | 757 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.balanced_multinomial_naive_bayes_v1.prediction_counts.Not Correct | 45 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.context_multinomial_naive_bayes_v1.accuracy | 0.818 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.context_multinomial_naive_bayes_v1.confusion.Correct.Correct | 635 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.context_multinomial_naive_bayes_v1.confusion.Correct.Not Correct | 61 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.context_multinomial_naive_bayes_v1.confusion.Not Correct.Correct | 85 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.context_multinomial_naive_bayes_v1.confusion.Not Correct.Not Correct | 21 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.context_multinomial_naive_bayes_v1.count | 802 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.context_multinomial_naive_bayes_v1.label_counts.Correct | 696 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.context_multinomial_naive_bayes_v1.label_counts.Not Correct | 106 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.context_multinomial_naive_bayes_v1.macro_f1 | 0.5601 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.context_multinomial_naive_bayes_v1.per_label.Correct.f1 | 0.8969 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.context_multinomial_naive_bayes_v1.per_label.Correct.precision | 0.8819 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.context_multinomial_naive_bayes_v1.per_label.Correct.recall | 0.9124 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.context_multinomial_naive_bayes_v1.per_label.Correct.support | 696 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.context_multinomial_naive_bayes_v1.per_label.Not Correct.f1 | 0.2234 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.context_multinomial_naive_bayes_v1.per_label.Not Correct.precision | 0.2561 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.context_multinomial_naive_bayes_v1.per_label.Not Correct.recall | 0.1981 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.context_multinomial_naive_bayes_v1.per_label.Not Correct.support | 106 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.context_multinomial_naive_bayes_v1.prediction_counts.Correct | 720 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.context_multinomial_naive_bayes_v1.prediction_counts.Not Correct | 82 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.majority_train_label.accuracy | 0.8678 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.majority_train_label.confusion.Correct.Correct | 696 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.majority_train_label.confusion.Correct.Not Correct | 0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.majority_train_label.confusion.Not Correct.Correct | 106 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.majority_train_label.confusion.Not Correct.Not Correct | 0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.majority_train_label.count | 802 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.majority_train_label.label_counts.Correct | 696 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.majority_train_label.label_counts.Not Correct | 106 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.majority_train_label.macro_f1 | 0.4646 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.majority_train_label.per_label.Correct.f1 | 0.9292 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.majority_train_label.per_label.Correct.precision | 0.8678 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.majority_train_label.per_label.Correct.recall | 1.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.majority_train_label.per_label.Correct.support | 696 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.majority_train_label.per_label.Not Correct.f1 | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.majority_train_label.per_label.Not Correct.precision | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.majority_train_label.per_label.Not Correct.recall | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.majority_train_label.per_label.Not Correct.support | 106 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.majority_train_label.prediction_counts.Correct | 802 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.multinomial_naive_bayes_v0.accuracy | 0.8653 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.multinomial_naive_bayes_v0.confusion.Correct.Correct | 691 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.multinomial_naive_bayes_v0.confusion.Correct.Not Correct | 5 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.multinomial_naive_bayes_v0.confusion.Not Correct.Correct | 103 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.multinomial_naive_bayes_v0.confusion.Not Correct.Not Correct | 3 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.multinomial_naive_bayes_v0.count | 802 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.multinomial_naive_bayes_v0.label_counts.Correct | 696 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.multinomial_naive_bayes_v0.label_counts.Not Correct | 106 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.multinomial_naive_bayes_v0.macro_f1 | 0.4901 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.multinomial_naive_bayes_v0.per_label.Correct.f1 | 0.9275 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.multinomial_naive_bayes_v0.per_label.Correct.precision | 0.8703 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.multinomial_naive_bayes_v0.per_label.Correct.recall | 0.9928 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.multinomial_naive_bayes_v0.per_label.Correct.support | 696 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.multinomial_naive_bayes_v0.per_label.Not Correct.f1 | 0.0526 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.multinomial_naive_bayes_v0.per_label.Not Correct.precision | 0.375 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.multinomial_naive_bayes_v0.per_label.Not Correct.recall | 0.0283 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.multinomial_naive_bayes_v0.per_label.Not Correct.support | 106 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.multinomial_naive_bayes_v0.prediction_counts.Correct | 794 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | baselines.multinomial_naive_bayes_v0.prediction_counts.Not Correct | 8 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | test_count | 802 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | test_paper_count | 17 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | train_count | 3079 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | train_label_counts.Correct | 2720 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | train_label_counts.Not Correct | 359 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | correctness | train_paper_count | 65 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_context_multinomial_naive_bayes_v2.accuracy | 0.9169 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_context_multinomial_naive_bayes_v2.confusion.Requires More.Requires More | 3 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_context_multinomial_naive_bayes_v2.confusion.Requires More.Sufficient | 39 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_context_multinomial_naive_bayes_v2.confusion.Sufficient.Requires More | 11 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_context_multinomial_naive_bayes_v2.confusion.Sufficient.Sufficient | 549 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_context_multinomial_naive_bayes_v2.count | 602 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_context_multinomial_naive_bayes_v2.label_counts.Requires More | 42 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_context_multinomial_naive_bayes_v2.label_counts.Sufficient | 560 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_context_multinomial_naive_bayes_v2.macro_f1 | 0.5318 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Requires More.f1 | 0.1071 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Requires More.precision | 0.2143 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Requires More.recall | 0.0714 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Requires More.support | 42 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Sufficient.f1 | 0.9564 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Sufficient.precision | 0.9337 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Sufficient.recall | 0.9804 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Sufficient.support | 560 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_context_multinomial_naive_bayes_v2.prediction_counts.Requires More | 14 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_context_multinomial_naive_bayes_v2.prediction_counts.Sufficient | 588 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_multinomial_naive_bayes_v1.accuracy | 0.9236 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_multinomial_naive_bayes_v1.confusion.Requires More.Requires More | 0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_multinomial_naive_bayes_v1.confusion.Requires More.Sufficient | 42 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_multinomial_naive_bayes_v1.confusion.Sufficient.Requires More | 4 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_multinomial_naive_bayes_v1.confusion.Sufficient.Sufficient | 556 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_multinomial_naive_bayes_v1.count | 602 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_multinomial_naive_bayes_v1.label_counts.Requires More | 42 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_multinomial_naive_bayes_v1.label_counts.Sufficient | 560 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_multinomial_naive_bayes_v1.macro_f1 | 0.4801 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_multinomial_naive_bayes_v1.per_label.Requires More.f1 | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_multinomial_naive_bayes_v1.per_label.Requires More.precision | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_multinomial_naive_bayes_v1.per_label.Requires More.recall | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_multinomial_naive_bayes_v1.per_label.Requires More.support | 42 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_multinomial_naive_bayes_v1.per_label.Sufficient.f1 | 0.9603 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_multinomial_naive_bayes_v1.per_label.Sufficient.precision | 0.9298 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_multinomial_naive_bayes_v1.per_label.Sufficient.recall | 0.9929 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_multinomial_naive_bayes_v1.per_label.Sufficient.support | 560 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_multinomial_naive_bayes_v1.prediction_counts.Requires More | 4 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.balanced_multinomial_naive_bayes_v1.prediction_counts.Sufficient | 598 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.context_multinomial_naive_bayes_v1.accuracy | 0.9169 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.context_multinomial_naive_bayes_v1.confusion.Requires More.Requires More | 2 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.context_multinomial_naive_bayes_v1.confusion.Requires More.Sufficient | 40 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.context_multinomial_naive_bayes_v1.confusion.Sufficient.Requires More | 10 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.context_multinomial_naive_bayes_v1.confusion.Sufficient.Sufficient | 550 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.context_multinomial_naive_bayes_v1.count | 602 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.context_multinomial_naive_bayes_v1.label_counts.Requires More | 42 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.context_multinomial_naive_bayes_v1.label_counts.Sufficient | 560 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.context_multinomial_naive_bayes_v1.macro_f1 | 0.5153 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.context_multinomial_naive_bayes_v1.per_label.Requires More.f1 | 0.0741 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.context_multinomial_naive_bayes_v1.per_label.Requires More.precision | 0.1667 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.context_multinomial_naive_bayes_v1.per_label.Requires More.recall | 0.0476 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.context_multinomial_naive_bayes_v1.per_label.Requires More.support | 42 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.context_multinomial_naive_bayes_v1.per_label.Sufficient.f1 | 0.9565 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.context_multinomial_naive_bayes_v1.per_label.Sufficient.precision | 0.9322 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.context_multinomial_naive_bayes_v1.per_label.Sufficient.recall | 0.9821 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.context_multinomial_naive_bayes_v1.per_label.Sufficient.support | 560 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.context_multinomial_naive_bayes_v1.prediction_counts.Requires More | 12 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.context_multinomial_naive_bayes_v1.prediction_counts.Sufficient | 590 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.evidence_aware_feature_logistic_v1.accuracy | 0.8771 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.evidence_aware_feature_logistic_v1.confusion.Requires More.Requires More | 10 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.evidence_aware_feature_logistic_v1.confusion.Requires More.Sufficient | 32 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.evidence_aware_feature_logistic_v1.confusion.Sufficient.Requires More | 42 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.evidence_aware_feature_logistic_v1.confusion.Sufficient.Sufficient | 518 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.evidence_aware_feature_logistic_v1.count | 602 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.evidence_aware_feature_logistic_v1.feature_count | 24 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.evidence_aware_feature_logistic_v1.label_counts.Requires More | 42 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.evidence_aware_feature_logistic_v1.label_counts.Sufficient | 560 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.evidence_aware_feature_logistic_v1.macro_f1 | 0.573 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.evidence_aware_feature_logistic_v1.per_label.Requires More.f1 | 0.2128 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.evidence_aware_feature_logistic_v1.per_label.Requires More.precision | 0.1923 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.evidence_aware_feature_logistic_v1.per_label.Requires More.recall | 0.2381 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.evidence_aware_feature_logistic_v1.per_label.Requires More.support | 42 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.evidence_aware_feature_logistic_v1.per_label.Sufficient.f1 | 0.9333 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.evidence_aware_feature_logistic_v1.per_label.Sufficient.precision | 0.9418 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.evidence_aware_feature_logistic_v1.per_label.Sufficient.recall | 0.925 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.evidence_aware_feature_logistic_v1.per_label.Sufficient.support | 560 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.evidence_aware_feature_logistic_v1.prediction_counts.Requires More | 52 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.evidence_aware_feature_logistic_v1.prediction_counts.Sufficient | 550 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.evidence_aware_feature_logistic_v1.probability_threshold | 0.6574 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.majority_train_label.accuracy | 0.9302 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.majority_train_label.confusion.Requires More.Requires More | 0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.majority_train_label.confusion.Requires More.Sufficient | 42 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.majority_train_label.confusion.Sufficient.Requires More | 0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.majority_train_label.confusion.Sufficient.Sufficient | 560 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.majority_train_label.count | 602 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.majority_train_label.label_counts.Requires More | 42 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.majority_train_label.label_counts.Sufficient | 560 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.majority_train_label.macro_f1 | 0.4819 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.majority_train_label.per_label.Requires More.f1 | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.majority_train_label.per_label.Requires More.precision | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.majority_train_label.per_label.Requires More.recall | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.majority_train_label.per_label.Requires More.support | 42 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.majority_train_label.per_label.Sufficient.f1 | 0.9639 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.majority_train_label.per_label.Sufficient.precision | 0.9302 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.majority_train_label.per_label.Sufficient.recall | 1.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.majority_train_label.per_label.Sufficient.support | 560 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.majority_train_label.prediction_counts.Sufficient | 602 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.multinomial_naive_bayes_v0.accuracy | 0.9302 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.multinomial_naive_bayes_v0.confusion.Requires More.Requires More | 0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.multinomial_naive_bayes_v0.confusion.Requires More.Sufficient | 42 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.multinomial_naive_bayes_v0.confusion.Sufficient.Requires More | 0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.multinomial_naive_bayes_v0.confusion.Sufficient.Sufficient | 560 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.multinomial_naive_bayes_v0.count | 602 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.multinomial_naive_bayes_v0.label_counts.Requires More | 42 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.multinomial_naive_bayes_v0.label_counts.Sufficient | 560 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.multinomial_naive_bayes_v0.macro_f1 | 0.4819 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.multinomial_naive_bayes_v0.per_label.Requires More.f1 | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.multinomial_naive_bayes_v0.per_label.Requires More.precision | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.multinomial_naive_bayes_v0.per_label.Requires More.recall | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.multinomial_naive_bayes_v0.per_label.Requires More.support | 42 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.multinomial_naive_bayes_v0.per_label.Sufficient.f1 | 0.9639 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.multinomial_naive_bayes_v0.per_label.Sufficient.precision | 0.9302 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.multinomial_naive_bayes_v0.per_label.Sufficient.recall | 1.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.multinomial_naive_bayes_v0.per_label.Sufficient.support | 560 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | baselines.multinomial_naive_bayes_v0.prediction_counts.Sufficient | 602 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | evidence_aware_features.mean_feature_weights.0.weight | 0.3305 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | evidence_aware_features.mean_feature_weights.1.weight | -0.2561 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | evidence_aware_features.mean_feature_weights.10.weight | -0.132 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | evidence_aware_features.mean_feature_weights.11.weight | 0.1112 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | evidence_aware_features.mean_feature_weights.2.weight | -0.2494 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | evidence_aware_features.mean_feature_weights.3.weight | -0.2247 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | evidence_aware_features.mean_feature_weights.4.weight | 0.2095 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | evidence_aware_features.mean_feature_weights.5.weight | -0.1952 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | evidence_aware_features.mean_feature_weights.6.weight | -0.1819 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | evidence_aware_features.mean_feature_weights.7.weight | 0.1693 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | evidence_aware_features.mean_feature_weights.8.weight | -0.1612 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | evidence_aware_features.mean_feature_weights.9.weight | -0.1343 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | test_count | 602 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | test_paper_count | 17 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | train_count | 2266 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | train_label_counts.Requires More | 158 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | train_label_counts.Sufficient | 2108 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | evidence | train_paper_count | 65 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.accuracy | 0.5546 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.confusion.Marginally Significant.Marginally Significant | 41 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.confusion.Marginally Significant.Not Significant | 0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.confusion.Marginally Significant.Significant | 147 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.confusion.Not Significant.Marginally Significant | 43 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.confusion.Not Significant.Not Significant | 0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.confusion.Not Significant.Significant | 51 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.confusion.Significant.Marginally Significant | 69 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.confusion.Significant.Not Significant | 0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.confusion.Significant.Significant | 345 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.count | 696 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.label_counts.Marginally Significant | 188 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.label_counts.Not Significant | 94 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.label_counts.Significant | 414 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.macro_f1 | 0.3205 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Marginally Significant.f1 | 0.2405 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Marginally Significant.precision | 0.268 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Marginally Significant.recall | 0.2181 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Marginally Significant.support | 188 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Not Significant.f1 | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Not Significant.precision | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Not Significant.recall | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Not Significant.support | 94 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Significant.f1 | 0.721 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Significant.precision | 0.6354 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Significant.recall | 0.8333 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.per_label.Significant.support | 414 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.prediction_counts.Marginally Significant | 153 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_context_multinomial_naive_bayes_v2.prediction_counts.Significant | 543 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.accuracy | 0.5589 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.confusion.Marginally Significant.Marginally Significant | 66 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.confusion.Marginally Significant.Not Significant | 4 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.confusion.Marginally Significant.Significant | 118 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.confusion.Not Significant.Marginally Significant | 39 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.confusion.Not Significant.Not Significant | 13 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.confusion.Not Significant.Significant | 42 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.confusion.Significant.Marginally Significant | 99 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.confusion.Significant.Not Significant | 5 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.confusion.Significant.Significant | 310 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.count | 696 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.label_counts.Marginally Significant | 188 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.label_counts.Not Significant | 94 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.label_counts.Significant | 414 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.macro_f1 | 0.4207 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.per_label.Marginally Significant.f1 | 0.3367 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.per_label.Marginally Significant.precision | 0.3235 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.per_label.Marginally Significant.recall | 0.3511 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.per_label.Marginally Significant.support | 188 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.per_label.Not Significant.f1 | 0.2241 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.per_label.Not Significant.precision | 0.5909 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.per_label.Not Significant.recall | 0.1383 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.per_label.Not Significant.support | 94 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.per_label.Significant.f1 | 0.7014 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.per_label.Significant.precision | 0.6596 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.per_label.Significant.recall | 0.7488 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.per_label.Significant.support | 414 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.prediction_counts.Marginally Significant | 204 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.prediction_counts.Not Significant | 22 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.balanced_multinomial_naive_bayes_v1.prediction_counts.Significant | 470 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.accuracy | 0.5833 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.confusion.Marginally Significant.Marginally Significant | 34 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.confusion.Marginally Significant.Not Significant | 0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.confusion.Marginally Significant.Significant | 154 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.confusion.Not Significant.Marginally Significant | 35 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.confusion.Not Significant.Not Significant | 0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.confusion.Not Significant.Significant | 59 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.confusion.Significant.Marginally Significant | 42 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.confusion.Significant.Not Significant | 0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.confusion.Significant.Significant | 372 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.count | 696 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.label_counts.Marginally Significant | 188 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.label_counts.Not Significant | 94 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.label_counts.Significant | 414 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.macro_f1 | 0.3241 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.per_label.Marginally Significant.f1 | 0.2274 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.per_label.Marginally Significant.precision | 0.3063 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.per_label.Marginally Significant.recall | 0.1809 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.per_label.Marginally Significant.support | 188 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.per_label.Not Significant.f1 | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.per_label.Not Significant.precision | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.per_label.Not Significant.recall | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.per_label.Not Significant.support | 94 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.per_label.Significant.f1 | 0.7447 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.per_label.Significant.precision | 0.6359 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.per_label.Significant.recall | 0.8986 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.per_label.Significant.support | 414 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.prediction_counts.Marginally Significant | 111 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.context_multinomial_naive_bayes_v1.prediction_counts.Significant | 585 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.accuracy | 0.5948 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.confusion.Marginally Significant.Marginally Significant | 0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.confusion.Marginally Significant.Not Significant | 0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.confusion.Marginally Significant.Significant | 188 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.confusion.Not Significant.Marginally Significant | 0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.confusion.Not Significant.Not Significant | 0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.confusion.Not Significant.Significant | 94 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.confusion.Significant.Marginally Significant | 0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.confusion.Significant.Not Significant | 0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.confusion.Significant.Significant | 414 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.count | 696 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.label_counts.Marginally Significant | 188 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.label_counts.Not Significant | 94 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.label_counts.Significant | 414 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.macro_f1 | 0.2486 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.per_label.Marginally Significant.f1 | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.per_label.Marginally Significant.precision | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.per_label.Marginally Significant.recall | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.per_label.Marginally Significant.support | 188 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.per_label.Not Significant.f1 | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.per_label.Not Significant.precision | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.per_label.Not Significant.recall | 0.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.per_label.Not Significant.support | 94 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.per_label.Significant.f1 | 0.7459 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.per_label.Significant.precision | 0.5948 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.per_label.Significant.recall | 1.0 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.per_label.Significant.support | 414 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.majority_train_label.prediction_counts.Significant | 696 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.accuracy | 0.5747 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.confusion.Marginally Significant.Marginally Significant | 45 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.confusion.Marginally Significant.Not Significant | 2 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.confusion.Marginally Significant.Significant | 141 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.confusion.Not Significant.Marginally Significant | 30 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.confusion.Not Significant.Not Significant | 6 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.confusion.Not Significant.Significant | 58 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.confusion.Significant.Marginally Significant | 63 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.confusion.Significant.Not Significant | 2 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.confusion.Significant.Significant | 349 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.count | 696 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.label_counts.Marginally Significant | 188 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.label_counts.Not Significant | 94 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.label_counts.Significant | 414 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.macro_f1 | 0.3723 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.per_label.Marginally Significant.f1 | 0.2761 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.per_label.Marginally Significant.precision | 0.3261 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.per_label.Marginally Significant.recall | 0.2394 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.per_label.Marginally Significant.support | 188 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.per_label.Not Significant.f1 | 0.1154 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.per_label.Not Significant.precision | 0.6 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.per_label.Not Significant.recall | 0.0638 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.per_label.Not Significant.support | 94 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.per_label.Significant.f1 | 0.7256 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.per_label.Significant.precision | 0.6369 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.per_label.Significant.recall | 0.843 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.per_label.Significant.support | 414 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.prediction_counts.Marginally Significant | 138 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.prediction_counts.Not Significant | 10 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | baselines.multinomial_naive_bayes_v0.prediction_counts.Significant | 548 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | test_count | 696 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | test_paper_count | 17 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | train_count | 2720 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | train_label_counts.Marginally Significant | 799 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | train_label_counts.Not Significant | 454 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | train_label_counts.Significant | 1467 | gold | peerreview_bench_baseline_metrics.json |
| PeerReview Bench | review_quality | verifier | significance | train_paper_count | 65 | gold | peerreview_bench_baseline_metrics.json |
| SubstanReview | substantiation | verifier | majority_train_label | test.accuracy | 0.5634 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | majority_train_label | test.confusion.Supported.Supported | 0 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | majority_train_label | test.confusion.Supported.Unsupported | 241 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | majority_train_label | test.confusion.Unsupported.Supported | 0 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | majority_train_label | test.confusion.Unsupported.Unsupported | 311 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | majority_train_label | test.count | 552 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | majority_train_label | test.label_counts.Supported | 241 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | majority_train_label | test.label_counts.Unsupported | 311 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | majority_train_label | test.macro_f1 | 0.3604 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | majority_train_label | test.per_label.Supported.f1 | 0.0 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | majority_train_label | test.per_label.Supported.precision | 0.0 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | majority_train_label | test.per_label.Supported.recall | 0.0 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | majority_train_label | test.per_label.Supported.support | 241 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | majority_train_label | test.per_label.Unsupported.f1 | 0.7207 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | majority_train_label | test.per_label.Unsupported.precision | 0.5634 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | majority_train_label | test.per_label.Unsupported.recall | 1.0 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | majority_train_label | test.per_label.Unsupported.support | 311 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | majority_train_label | test.prediction_counts.Unsupported | 552 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | test.accuracy | 0.6467 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | test.confusion.Supported.Supported | 144 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | test.confusion.Supported.Unsupported | 97 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | test.confusion.Unsupported.Supported | 98 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | test.confusion.Unsupported.Unsupported | 213 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | test.count | 552 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | test.label_counts.Supported | 241 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | test.label_counts.Unsupported | 311 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | test.macro_f1 | 0.6411 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | test.per_label.Supported.f1 | 0.5963 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | test.per_label.Supported.precision | 0.595 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | test.per_label.Supported.recall | 0.5975 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | test.per_label.Supported.support | 241 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | test.per_label.Unsupported.f1 | 0.686 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | test.per_label.Unsupported.precision | 0.6871 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | test.per_label.Unsupported.recall | 0.6849 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | test.per_label.Unsupported.support | 311 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | test.prediction_counts.Supported | 242 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | test.prediction_counts.Unsupported | 310 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | train.accuracy | 0.8476 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | train.confusion.Supported.Supported | 788 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | train.confusion.Supported.Unsupported | 203 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | train.confusion.Unsupported.Supported | 136 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | train.confusion.Unsupported.Unsupported | 1098 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | train.count | 2225 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | train.label_counts.Supported | 991 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | train.label_counts.Unsupported | 1234 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | train.macro_f1 | 0.8446 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | train.per_label.Supported.f1 | 0.823 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | train.per_label.Supported.precision | 0.8528 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | train.per_label.Supported.recall | 0.7952 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | train.per_label.Supported.support | 991 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | train.per_label.Unsupported.f1 | 0.8663 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | train.per_label.Unsupported.precision | 0.844 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | train.per_label.Unsupported.recall | 0.8898 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | train.per_label.Unsupported.support | 1234 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | train.prediction_counts.Supported | 924 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | multinomial_naive_bayes_v0 | train.prediction_counts.Unsupported | 1301 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | test.accuracy | 0.5109 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | test.confusion.Supported.Supported | 124 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | test.confusion.Supported.Unsupported | 117 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | test.confusion.Unsupported.Supported | 153 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | test.confusion.Unsupported.Unsupported | 158 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | test.count | 552 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | test.label_counts.Supported | 241 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | test.label_counts.Unsupported | 311 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | test.macro_f1 | 0.509 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | test.per_label.Supported.f1 | 0.4788 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | test.per_label.Supported.precision | 0.4477 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | test.per_label.Supported.recall | 0.5145 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | test.per_label.Supported.support | 241 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | test.per_label.Unsupported.f1 | 0.5392 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | test.per_label.Unsupported.precision | 0.5745 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | test.per_label.Unsupported.recall | 0.508 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | test.per_label.Unsupported.support | 311 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | test.prediction_counts.Supported | 277 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | test.prediction_counts.Unsupported | 275 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | train.accuracy | 0.5429 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | train.confusion.Supported.Supported | 491 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | train.confusion.Supported.Unsupported | 500 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | train.confusion.Unsupported.Supported | 517 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | train.confusion.Unsupported.Unsupported | 717 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | train.count | 2225 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | train.label_counts.Supported | 991 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | train.label_counts.Unsupported | 1234 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | train.macro_f1 | 0.5382 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | train.per_label.Supported.f1 | 0.4912 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | train.per_label.Supported.precision | 0.4871 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | train.per_label.Supported.recall | 0.4955 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | train.per_label.Supported.support | 991 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | train.per_label.Unsupported.f1 | 0.5851 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | train.per_label.Unsupported.precision | 0.5892 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | train.per_label.Unsupported.recall | 0.581 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | train.per_label.Unsupported.support | 1234 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | train.prediction_counts.Supported | 1008 | gold | substanreview_baseline_metrics.json |
| SubstanReview | substantiation | verifier | transparent_context_cue_v0 | train.prediction_counts.Unsupported | 1217 | gold | substanreview_baseline_metrics.json |
| live-verification | review_audit | agent_rag | manifest | run_count | 1 | silver | manifest:experiment-3fdada1023284a3c97a8bda2de737ad3 |
| live-verification | review_audit | agent_rag | manifest | run_count | 1 | silver | manifest:experiment-ecacc04ef1cf4503920f329e57eb8cc8 |
| live-verification | review_audit | agent_rag | manifest | succeeded_rate | 1.0 | silver | manifest:experiment-3fdada1023284a3c97a8bda2de737ad3 |
| live-verification | review_audit | agent_rag | manifest | succeeded_rate | 1.0 | silver | manifest:experiment-ecacc04ef1cf4503920f329e57eb8cc8 |
| live-verification | review_audit | agent_rag | manifest | succeeded_run_count | 1 | silver | manifest:experiment-3fdada1023284a3c97a8bda2de737ad3 |
| live-verification | review_audit | agent_rag | manifest | succeeded_run_count | 1 | silver | manifest:experiment-ecacc04ef1cf4503920f329e57eb8cc8 |
| live-verification | review_audit | generation | manifest | weakness_count | 0 | silver | manifest:experiment-3fdada1023284a3c97a8bda2de737ad3 |
| live-verification | review_audit | generation | manifest | weakness_count | 0 | silver | manifest:experiment-ecacc04ef1cf4503920f329e57eb8cc8 |
| live-verification | review_audit | ranking | manifest | ranked_finding_count | 0 | silver | manifest:experiment-3fdada1023284a3c97a8bda2de737ad3 |
| live-verification | review_audit | ranking | manifest | ranked_finding_count | 0 | silver | manifest:experiment-ecacc04ef1cf4503920f329e57eb8cc8 |
