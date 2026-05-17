def standing_controller(x_com, x_dot, x_ref, kp, kd):
    """
    τ = Kp(x_ref - x_com) - Kd * x_dot
    """
    return kp * (x_ref - x_com) - kd * x_dot
