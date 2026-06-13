from evireview.models.evidence import EvidenceBlock


def apply_structure_priors(
    *,
    expected_sections: list[str],
    expected_types: list[str],
    candidates: list[dict],
    section_weight: float,
    evidence_type_weight: float,
) -> list[dict]:
    ranked = []
    for candidate in candidates:
        item = dict(candidate)
        item["score"] += section_weight if item["section"] in expected_sections else 0.0
        item["score"] += evidence_type_weight if item["type"] in expected_types else 0.0
        ranked.append(item)
    return sorted(ranked, key=lambda item: (-item["score"], item["id"]))


def expand_neighbors(
    blocks: list[EvidenceBlock],
    *,
    seed_ids: list[str],
    radius: int,
) -> list[EvidenceBlock]:
    by_id = {block.block_id: block for block in blocks}
    by_ordinal = {block.ordinal: block for block in blocks}
    selected: dict[str, EvidenceBlock] = {}
    for seed_id in seed_ids:
        seed = by_id[seed_id]
        selected[seed.block_id] = seed
        for ordinal in range(seed.ordinal - radius, seed.ordinal + radius + 1):
            neighbor = by_ordinal.get(ordinal)
            if neighbor is not None and neighbor.section == seed.section:
                selected[neighbor.block_id] = neighbor
    return sorted(selected.values(), key=lambda block: block.ordinal)
