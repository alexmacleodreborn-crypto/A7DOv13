import math

def capture_point(x, x_dot, g, l):
    omega = math.sqrt(g / l)
    return x + x_dot / omega
