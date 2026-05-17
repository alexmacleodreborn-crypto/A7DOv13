# dna.py
def init_dna():
    return {
        "limb_lengths": {k: 0.01 for k in ["thigh", "shank", "foot", "torso", "upperarm", "forearm"]},
        "muscle_strength": {k: 0.1 for k in ["hip", "knee", "ankle", "shoulder", "elbow"]},
        "ATP_max": 10,
        "growth_stage": 0
    }

def grow(dna):
    for limb in dna["limb_lengths"]:
        dna["limb_lengths"][limb] += 0.01
    for muscle in dna["muscle_strength"]:
        dna["muscle_strength"][muscle] += 0.1
    dna["ATP_max"] += 1
    # Stage transitions
    if dna["limb_lengths"]["thigh"] > 0.1 and dna["growth_stage"] == 0:
        dna["growth_stage"] = 1
    if dna["limb_lengths"]["thigh"] > 0.12 and dna["growth_stage"] == 1:
        dna["growth_stage"] = 2
    if dna["limb_lengths"]["torso"] > 0.18 and dna["growth_stage"] == 2:
        dna["growth_stage"] = 3
    return dna

def developmental_mode(dna):
    stages = ["emwomb", "sit", "crawl", "stand", "walk", "run"]
    return stages[dna["growth_stage"]]
