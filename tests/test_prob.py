from boxing.models import Boxer
from boxing.prob import block_score, dodge_score, parry_score

def make_boxer(base: int) -> Boxer:
    return Boxer(
        jab=base, straight=base, lead_hook=base, hook=base,
        lead_uppercut=base, uppercut=base, blocking=base, accuracy=base,
        anticipation=base, composure=base, positioning=base, decision=base,
        aggression=base, focus=base, workrate=base, planning=base,
        power=base, hand_speed=base, foot_speed=base,
        reflexes=base, stamina=base, agility=base,
        name="X",
    )

def test_defence_scores_monotonic():
    low, mid, high = make_boxer(5), make_boxer(10), make_boxer(15)
    assert block_score(low)  < block_score(mid)  < block_score(high)
    assert dodge_score(low)  < dodge_score(mid)  < dodge_score(high)
    assert parry_score(low)  < parry_score(mid)  < parry_score(high)