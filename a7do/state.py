from dataclasses import dataclass

@dataclass
class A7DOState:
    # COM state
    x_com: float = 0.0
    x_com_dot: float = 0.0

    # Torso angle (for display / extension)
    theta: float = 0.0
    theta_dot: float = 0.0

    # Energy
    atp: float = 100.0
    atp_max: float = 100.0

    # Support
    bos_left: float = -0.1
    bos_right: float = 0.1

    # Gait
    gait_phase: float = 0.0
    stance_foot: str = "L"

    # Development
    stage: str = "stand"
