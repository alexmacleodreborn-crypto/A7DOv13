def walk_reference(x_center, bos_width, alpha=0.7):
    """
    Bias the standing reference to intentionally
    push capture point outside BOS.
    """
    return x_center + alpha * bos_width
