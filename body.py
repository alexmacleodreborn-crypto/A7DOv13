# body.py
def default_body():
    return {
        "limb_lengths": {
            "thigh": 0.12, "shank": 0.12, "foot": 0.08,
            "torso": 0.18, "upperarm": 0.10, "forearm": 0.10
        },
        "segment_mass": {
            "thigh": 3.5, "shank": 1.6, "foot": 1.0,
            "torso": 20.0, "head": 5.0,
            "upperarm": 1.2, "forearm": 1.0
        }
    }
