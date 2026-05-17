def walk_bias(x_ref, bos_width, alpha=0.7):
    """
    Intentional destabilisation for walk initiation
    """
    return x_ref + alpha * bos_width
