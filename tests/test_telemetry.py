from boxing.engine import MatchEngine
from .test_engine import make_boxer  # reuse helper

def test_round_telemetry_shape():
    a = make_boxer("A", base=10)
    b = make_boxer("B", base=10)
    out = MatchEngine(a, b, seed=123).simulate()

    rounds = out["rounds"]
    assert len(rounds) == 12

    for rs in rounds:
        # each round: 2 throws per boxer
        assert sum(rs["red"]["thrown"].values()) == 2
        assert sum(rs["blue"]["thrown"].values()) == 2

        # defence counts reflect how many times each boxer defended (2 each)
        assert sum(rs["red"]["defence"].values()) == 2
        assert sum(rs["blue"]["defence"].values()) == 2

        # landed cannot exceed thrown (per boxer)
        assert sum(rs["red"]["landed"].values()) <= 2
        assert sum(rs["blue"]["landed"].values()) <= 2
