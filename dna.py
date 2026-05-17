def init_dna():
    return {
        "limb_lengths": {k: 0.0 for k in ["thigh", "shank", "foot", "torso", "upperarm", "forearm"]},
        "organ_development": {"spine": 0.0, "heart": 0.0, "lungs": 0.0, "umbilical_cord": 1.0},
        "muscle_strength": {k: 0.0 for k in ["hip", "knee", "ankle", "shoulder", "elbow"]},
        "ATP_max": 0.0,
        "heartbeat": False,
        "breathing": False,
        "growth_stage": 0
    }

def grow(DNA, dt=1):
    # Neural tube (spine) forms first
    DNA["organ_development"]["spine"] = min(1.0, DNA["organ_development"]["spine"] + 0.01 * dt)
    # Heart forms after neural tube threshold
    if DNA["organ_development"]["spine"] > 0.2:
        DNA["organ_development"]["heart"] = min(1.0, DNA["organ_development"]["heart"] + 0.02 * dt)
        if DNA["organ_development"]["heart"] > 0.3:
            DNA["heartbeat"] = True
    # Head/body/limbs grow after heart threshold
    if DNA["organ_development"]["heart"] > 0.3:
        for limb in DNA["limb_lengths"]:
            DNA["limb_lengths"][limb] += 0.01 * dt
        for muscle in DNA["muscle_strength"]:
            DNA["muscle_strength"][muscle] += 0.1 * dt
        DNA["ATP_max"] += 1 * dt
        # Lungs grow after torso threshold
        if DNA["limb_lengths"]["torso"] > 0.1:
            DNA["organ_development"]["lungs"] = min(1.0, DNA["organ_development"]["lungs"] + 0.015 * dt)
            if DNA["organ_development"]["lungs"] > 0.8 and DNA["organ_development"]["umbilical_cord"] == 0.0:
                DNA["breathing"] = True
    # Cord detachment after spine threshold
    if DNA["organ_development"]["spine"] > 0.7:
        DNA["organ_development"]["umbilical_cord"] = 0.0
    # Stage transitions
    if DNA["organ_development"]["spine"] > 0.2 and DNA["organ_development"]["heart"] > 0.3 and DNA["limb_lengths"]["thigh"] > 0.1 and DNA["growth_stage"] == 0:
        DNA["growth_stage"] = 1
    if DNA["limb_lengths"]["thigh"] > 0.12 and DNA["growth_stage"] == 1:
        DNA["growth_stage"] = 2
    if DNA["limb_lengths"]["torso"] > 0.18 and DNA["growth_stage"] == 2:
        DNA["growth_stage"] = 3
    if DNA["limb_lengths"]["torso"] > 0.20 and DNA["growth_stage"] == 3:
        DNA["growth_stage"] = 4
    if DNA["limb_lengths"]["torso"] > 0.22 and DNA["growth_stage"] == 4:
        DNA["growth_stage"] = 5
    return DNA

def developmental_mode(DNA):
    stages = ["emwomb", "sit", "crawl", "stand", "walk", "run"]
    return stages[DNA["growth_stage"]]
