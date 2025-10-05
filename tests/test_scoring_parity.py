from ra9.memory import score_candidate


def test_score_candidate_monotonic_with_distance_and_age():
    s1 = score_candidate(distance=0.1, importance=0.5, ts=0, now_ts=60*60*24*100)  # old
    s2 = score_candidate(distance=0.1, importance=0.5, ts=60*60*24*99, now_ts=60*60*24*100)  # newer
    assert s2 > s1
    s3 = score_candidate(distance=0.2, importance=0.5, ts=60*60*24*99, now_ts=60*60*24*100)
    assert s3 < s2

