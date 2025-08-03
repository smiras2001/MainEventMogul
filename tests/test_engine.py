from boxing.engine import MatchEngine
from boxing.models import Boxer

red = Boxer("A", 10, 10, 10, 10, 10, 10)
blue = Boxer("B", 10, 10, 10, 10, 10, 10)


def test_seed_reproducibility():
    out1 = MatchEngine(red, blue, seed=123).simulate()
    out2 = MatchEngine(red, blue, seed=123).simulate()
    assert out1 == out2


def test_skill_bounds():
    try:
        Boxer("Bad", 0, 21, 5, 5, 5, 5)
    except ValueError:
        assert True
    else:
        assert False