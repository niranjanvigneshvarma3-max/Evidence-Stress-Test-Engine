# Evidence Stress-Test Engine

A pure Python companion extracted from [TraceMind](https://github.com/niranjanvigneshvarma3-max/TraceMind)'s signature evidence board. It is independently runnable and uses synthetic data. It demonstrates citation location checks and how removing evidence changes a transparent ranking. It does not generate claims or prove causation.

## Run

- `python3 demo.py --exclude retry-change` shows baseline and changed rankings.
- `python3 -m unittest discover -s tests -v` checks citation rejection, ranking changes, remaining contradictions, and source dependence.

`engine.py` validates that cited evidence IDs exist and locations fit the source document. It then computes `supporting count - contradicting count` from active evidence. Excluding an item does not call a model. A hypothesis with at least two supporting items receives a dependence flag when 75% or more of its active support comes from one document.

The score is a **heuristic support count**, never a probability or proof. A citation can point to a real page or row while still failing to support a model's wording. TraceMind adds source documents, a web UI, database storage, and model output; this repo isolates the deterministic part for learning and testing.

GitHub Actions runs the unit tests on each push. This learning project was built with AI coding assistance; the transparent scoring rule and known limits are documented so reviewers can inspect what the demo actually establishes.
