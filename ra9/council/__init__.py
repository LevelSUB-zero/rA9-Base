"""Council System package for RA9.

Modules:
- schemas: Pydantic models for council system objects
- aggregator: scoring and decision logic
- query_analyzer: derives context weights and worker selection
- workers: mock worker generators (MVP)
- councils: mock council evaluators (MVP)
- safety: lightweight safety pre-filters
- synthesis: synthesis engine stubs
- trust: trust and calibration utilities
- pipeline: end-to-end orchestration of the council flow
"""

from . import schemas, aggregator, query_analyzer, workers, councils, safety, synthesis, trust, pipeline  # noqa: F401


