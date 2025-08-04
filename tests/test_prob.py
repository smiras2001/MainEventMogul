import random

import pytest

from boxing.prob import hit


def test_equal_skills_about_half():
    rng = random.Random(0)
    hits = sum(hit(10, 10, 10, rng=rng) for _ in range(1000))
    assert 450 < hits < 550


def test_extremes():
    always = sum(hit(20, 1, 1, rng=random.Random(0)) for _ in range(500))
    never = sum(hit(1, 20, 20, rng=random.Random(0)) for _ in range(500))
    assert always >= 470  # ~94 % of 500
    assert never <= 30
