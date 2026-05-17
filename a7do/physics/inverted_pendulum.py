import math

def step_inverted_pendulum(x, x_dot, x_foot, g, l, dt):
    """
    x_ddot = (g/l) * (x - x_foot)
    """
    x_ddot = (g / l) * (x - x_foot)
    x_dot += x_ddot * dt
    x += x_dot * dt
    return x, x_dot
