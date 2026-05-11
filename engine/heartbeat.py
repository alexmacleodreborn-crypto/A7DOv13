# engine/heartbeat.py
from typing import List
from engine.state import A7DOState
from engine.torque_bus import TorqueBus, merge_torque_fields, apply_constraints
from physics.physics_engine import physics_step

class Heartbeat:
    def __init__(self, layers: List, physics_engine=None, logger=None):
        self.layers = layers
        self.bus = TorqueBus()
        self.physics_engine = physics_engine
        self.logger = logger

    def tick(self, state: A7DOState, world: dict, dt: float) -> A7DOState:
        # 1. Observe
        for layer in self.layers:
            layer.observe(state)

        # 2. Clear torque bus
        self.bus.clear()

        # 3. Update + publish
        for layer in self.layers:
            layer.update(state, dt)
            layer.publish(state, self.bus, dt)

        # 4. Merge torque fields
        metrics = state.S_cog
        tau_total = merge_torque_fields(self.bus, state, metrics)

        # 5. Apply constraints
        tau_constrained = apply_constraints(tau_total, state.S_phys)

        # 6. Physics step (world)
        if self.physics_engine is not None:
            state = physics_step(self.physics_engine, state, tau_constrained, dt)

        # 7. Logging
        if self.logger:
            self.logger.log_tick(state)

        return state
