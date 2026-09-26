"""Pure Python citation validation and reversible evidence stress testing."""

from copy import deepcopy


def valid_evidence(evidence: dict, documents: dict[str, dict]) -> bool:
    document = documents.get(evidence.get("document_id"))
    if not document:
        return False
    kind = document.get("kind")
    if kind == "pdf":
        return isinstance(evidence.get("page"), int) and 1 <= evidence["page"] <= document["pages"]
    if kind == "csv":
        return isinstance(evidence.get("row"), int) and 2 <= evidence["row"] <= document["rows"] + 1
    return kind == "text" and bool(evidence.get("locator"))


def validate(hypotheses: list[dict], evidence: list[dict], documents: dict[str, dict]) -> tuple[list[dict], list[str]]:
    valid_ids = {item["id"] for item in evidence if valid_evidence(item, documents)}
    clean = []
    invalid = set()
    for hypothesis in hypotheses:
        candidate = deepcopy(hypothesis)
        for field in ("supporting_ids", "contradicting_ids"):
            invalid.update(set(candidate[field]) - valid_ids)
            candidate[field] = list(dict.fromkeys(item_id for item_id in candidate[field] if item_id in valid_ids))
        if candidate["supporting_ids"]:
            clean.append(candidate)
    return clean, sorted(invalid)


def rank(hypotheses: list[dict], evidence: list[dict], excluded: set[str] | None = None) -> list[dict]:
    """Heuristic support count minus contradiction count; no LLM call or probability."""
    excluded = excluded or set()
    by_id = {item["id"]: item for item in evidence}
    rows = []
    for hypothesis in hypotheses:
        supporting = [item_id for item_id in hypothesis["supporting_ids"]
                      if item_id in by_id and item_id not in excluded]
        contradicting = [item_id for item_id in hypothesis["contradicting_ids"]
                         if item_id in by_id and item_id not in excluded]
        source_counts: dict[str, int] = {}
        for item_id in supporting:
            source = by_id[item_id]["document_id"]
            source_counts[source] = source_counts.get(source, 0) + 1
        share = max(source_counts.values(), default=0) / len(supporting) if supporting else 0
        rows.append({"title": hypothesis["title"], "score": len(supporting) - len(contradicting),
                     "supporting": len(supporting), "contradicting": len(contradicting),
                     "single_source_dependent": len(supporting) >= 2 and share >= 0.75,
                     "excluded_links": sorted(excluded & set(hypothesis["supporting_ids"] + hypothesis["contradicting_ids"]))})
    return sorted(rows, key=lambda row: (-row["score"], row["title"].casefold()))
