# engine/state.py
from typing import Dict, List, Any
import dataclasses

@dataclasses.dataclass
class SPhys:
    # Physical state of the body in the world
    joint_positions: List[float]
    joint_velocities: List[float]
    joint_torques_applied: List[float]

    segment_poses: List[Any]          # future: full kinematic tree
    contact_points: List[Any]

    com: List[float]                  # organism's internal CoM estimate [x, y, z]
    support_polygon: List[List[float]]# internal estimate of support region
    stability_flags: Dict[str, bool]  # e.g. {"is_stable": True}

@dataclasses.dataclass
class A7DOState:
    # Core organism state, all internal
    S_phys: SPhys
    S_osc: Dict[str, Any]
    S_cog: Dict[str, Any]
    S_int: Dict[str, Any]
    S_learn: Dict[str, Any]
    S_LTM: Dict[str, Any]
    S_mot: Dict[str, Any]
    S_soc: Dict[str, Any]
    S_mind: Dict[str, Any]
    S_meta: Dict[str, Any]

    C: float                 # developmental level
    Omega_global: float      # global coherence / arousal

    tau_fields: Dict[str, Any]
    tau_weights: Dict[str, Any]
    tau_total: List[float]

    logs: Dict[str, Any]
