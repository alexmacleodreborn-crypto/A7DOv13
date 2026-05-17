import math

def update_gait_phase(phi, omega, dt):
    phi += omega * dt
    if phi >= 2 * math.pi:
        phi -= 2 * math.pi
    return phi


def swing_leg_target(phi, step_length):
    """
    Simple forward swing trajectory.
    """
    return step_length * math.sin(phi)
