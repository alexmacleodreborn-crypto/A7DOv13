import math

def update_gait_phase(phi, omega, dt):
    phi += omega * dt
    if phi > 2 * math.pi:
        phi -= 2 * math.pi
    return phi
