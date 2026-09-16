from face_insight.face_analysis import aggregate_scores
from face_insight.storage import calculate_average


def test_aggregate_scores():
    counts = aggregate_scores([0, 1, 3, 3, 10])
    assert counts == [1, 1, 0, 2, 0, 0, 0, 0, 0, 0, 1]


def test_average_only_counts_faces():
    counts = [0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 1]
    assert calculate_average(counts) == 4.25


def test_average_with_no_face_does_not_divide_by_zero():
    assert calculate_average([3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) is None
