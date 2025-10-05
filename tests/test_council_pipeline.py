from ra9.council.pipeline import CouncilPipeline
from ra9.council.schemas import QueryContext


def test_pipeline_basic():
    pipe = CouncilPipeline()
    ctx = QueryContext(
        queryId="q-1",
        userId="u-1",
        text="Explain photosynthesis for an 8-year-old",
        mode="concise",
        loopDepth=1,
        allowMemoryWrite=False,
        userPrefs={"tone": "friendly", "clarity": "high"},
    )
    res = pipe.run(ctx)
    assert res.decision in {"select", "synthesize", "re_eval", "fallback"}
    assert res.finalText is None or isinstance(res.finalText, str)


