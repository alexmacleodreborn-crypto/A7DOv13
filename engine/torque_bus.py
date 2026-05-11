# engine/torque_bus.py
from typing import List, Dict, Any
import dataclasses

@dataclasses.dataclass
class TorqueField:
    id: str
    joints: List[int]
    tau: List[float]
    priority: float = 0.5
    metadata: Dict[str, Any] = dataclasses.field(default_factory=dict)

class TorqueBus:
    def __init__(self):
        self.fields: List[TorqueField] = []

    def clear(self):
        self.fields.clear()

    def publish(self, field: TorqueField):
        self.fields.append(field)

    def get_fields_for_joint(self, joint_id: int) -> List[TorqueField]:
        return [f for f in self.fields if joint_id in f.joints]


def merge_torque_fields(bus: TorqueBus, state, metrics) -> Dict[int, float]:
    """
    Merge all published torque fields into a single torque vector.
    Weighted by priority, coherence, and meta-modulation.
    """
    tau_total: Dict[int, float] = {}
    num_joints = len(state.S_phys.joint_positions)

    for joint_id in range(num_joints):
        fields = bus.get_fields_for_joint(joint_id)
        if not fields:
            tau_total[joint_id] = 0.0
            continue

        weighted_sum = 0.0
        total_weight = 0.0

        for field in fields:
            w = compute_weight(field, joint_id, state, metrics)
            tau_value = field.tau[field.joints.index(joint_id)]
            weighted_sum += w * tau_value
            total_weight += w

        tau_total[joint_id] = weighted_sum / total_weight if total_weight > 0 else 0.0

    state.tau_total = [tau_total[j] for j in sorted(tau_total.keys())]
    return tau_total


def compute_weight(field: TorqueField, joint_id: int, state, metrics) -> float:
    """
    Influence weight for a torque field.
    """
    active_layers = state.S_meta.get("active_layers", [])
    gating = 1.0 if field.id in active_layers else 0.5

    kappa = metrics.get("kappa", 1.0)
    omega = state.Omega_global if state.Omega_global is not None else 1.0
    priority = field.priority
    meta_mod = state.S_meta.get("torque_weight_modulation", 1.0)

    return gating * kappa * omega * priority * meta_mod


def apply_constraints(tau_total: Dict[int, float], S_phys) -> Dict[int, float]:
    """
    Clamp torques to human-plausible limits and apply damping.
    """
    constrained: Dict[int, float] = {}
    torque_limit = 150.0      # Nm, placeholder but realistic order of magnitude
    damping_factor = 0.95

    for joint_id, tau in tau_total.items():
        tau_clamped = max(-torque_limit, min(torque_limit, tau))
        tau_damped = tau_clamped * damping_factor
        constrained[joint_id] = tau_damped

    return constrained
