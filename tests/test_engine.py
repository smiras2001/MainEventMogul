from boxing.engine import MatchEngine
from boxing.models import Boxer

a = Boxer("A", 10, 10, 10, 10, 10, 10, block=10, accuracy=10, power=10, reflexes=10)
b = Boxer("B", 10, 10, 10, 10, 10, 10, block=10, accuracy=10, power=10, reflexes=10)


def test_seed_reproducible():
    out1 = MatchEngine(a, b, seed=123).simulate()
    out2 = MatchEngine(a, b, seed=123).simulate()
    assert out1 == out2
