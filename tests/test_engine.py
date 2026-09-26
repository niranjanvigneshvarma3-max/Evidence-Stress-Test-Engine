import json
import unittest
from pathlib import Path

from engine import rank, validate, valid_evidence


CASE = json.loads((Path(__file__).resolve().parents[1] / "sample_case.json").read_text())


class EngineTests(unittest.TestCase):
    def test_citation_location_rejects_wrong_pdf_page_and_csv_row(self):
        self.assertFalse(valid_evidence({"document_id": "deployment.pdf", "page": 2}, CASE["documents"]))
        self.assertFalse(valid_evidence({"document_id": "api_log.csv", "row": 20}, CASE["documents"]))

    def test_unknown_citation_is_removed(self):
        item = {"title": "test", "supporting_ids": ["retry-change", "invented"], "contradicting_ids": []}
        clean, invalid = validate([item], CASE["evidence"], CASE["documents"])
        self.assertEqual(invalid, ["invented"])
        self.assertEqual(clean[0]["supporting_ids"], ["retry-change"])

    def test_exclusion_changes_rank_and_preserves_contradiction(self):
        clean, _ = validate(CASE["hypotheses"], CASE["evidence"], CASE["documents"])
        self.assertEqual(rank(clean, CASE["evidence"])[0]["title"], "Retry amplification")
        after = rank(clean, CASE["evidence"], {"retry-change"})
        self.assertEqual(after[0]["title"], "Gateway instability")
        retry = next(row for row in after if row["title"] == "Retry amplification")
        self.assertEqual(retry["contradicting"], 1)
        self.assertEqual(retry["excluded_links"], ["retry-change"])

    def test_single_source_dependence(self):
        clean, _ = validate(CASE["hypotheses"], CASE["evidence"], CASE["documents"])
        gateway = next(row for row in rank(clean, CASE["evidence"]) if row["title"] == "Gateway instability")
        self.assertTrue(gateway["single_source_dependent"])


if __name__ == "__main__":
    unittest.main()
