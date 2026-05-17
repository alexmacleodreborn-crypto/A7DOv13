def stages():
    return ["emwomb", "sit", "crawl", "stand", "walk", "run"]

def stage_from_growth(growth_stage):
    return stages()[growth_stage]
