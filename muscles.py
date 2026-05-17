# muscles.py
def default_muscles():
    return {
        "muscle_strength": {
            "hip": 0.1, "knee": 0.1, "ankle": 0.1,
            "shoulder": 0.1, "elbow": 0.1
        },
        "ATP_max": 10,
        "activation": {joint: 0.5 for joint in ["hip", "knee", "ankle", "shoulder", "elbow"]},
        "fatigue": 1.0
    }

def muscle_force(Fmax, activation, fatigue):
    return Fmax * activation * fatigue
