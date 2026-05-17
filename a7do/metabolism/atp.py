def drain_atp(atp, effort, dt):
    return max(0.0, atp - effort * dt)
