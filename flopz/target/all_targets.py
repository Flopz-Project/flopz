"""
a list of all implemented targets
Add your own target to this list so it gets discovered by scripts/flopz_instrument.py
"""
from flopz.target.bolero.bolero_target import BoleroTarget

_all_targets = [
    BoleroTarget
]

def get_target_by_name(name: str):
    for t in _all_targets:
        if t.name() == name:
            return t