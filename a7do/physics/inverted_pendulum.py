def step_inverted_pendulum(x, x_dot, x_support, tau, g, l, m, dt):
    """
    Controlled linear inverted pendulum:
    x_ddot = (g/l)(x - x_support) + tau/(ml)
    """
    x_ddot = (g / l) * (x - x_support) + tau / (m * l)
    x_dot += x_ddot * dt
    x += x_dot * dt
    return x, x_dot
