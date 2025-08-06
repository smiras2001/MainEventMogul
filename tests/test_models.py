from boxing.models import Boxer
import pytest

def test_boxer_validation_ok():
    _ = Boxer(
        # Fundamentals
        jab=15, straight=15, lead_hook=15, hook=15,
        lead_uppercut=15, uppercut=15, blocking=15, accuracy=15,
        # Boxing IQ
        anticipation=15, composure=15, positioning=15, decision=15,
        aggression=15, focus=15, workrate=15, planning=15,
        # Athleticism
        power=15, hand_speed=15, foot_speed=15,
        reflexes=15, stamina=15, agility=15,
    )

def test_boxer_validation_fail():
    with pytest.raises(ValueError):
        Boxer(
            # jab out of range triggers failure
            jab=0, straight=15, lead_hook=15, hook=15,
            lead_uppercut=15, uppercut=15, blocking=15, accuracy=15,
            anticipation=15, composure=15, positioning=15, decision=15,
            aggression=15, focus=15, workrate=15, planning=15,
            power=15, hand_speed=15, foot_speed=15,
            reflexes=15, stamina=15, agility=15,
        )
