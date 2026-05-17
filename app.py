import math
import streamlit as st

from a7do.state import A7DOState
from a7do.physics.inverted_pendulum import step_inverted_pendulum
from a7do.control.standing import standing_controller
from a7do.control.recovery import capture_point
from a7do.control.walk_init import walk_reference
from a7do.control.gait import update_gait_phase

# --------------------------------------------------
# Streamlit setup
# --------------------------------------------------
st.set_page_config(layout="wide")
st.title("A7DOv13 — Standing → Walking (Closed Loop)")

# --------------------------------------------------
# Initialise state
# --------------------------------------------------
if "state" not in st.session_state:
    st.session_state.state = A7DOState()

if "t" not in st.session_state:
    st.session_state.t = 0.0

state = st.session_state.state

# --------------------------------------------------
# Parameters
# --------------------------------------------------
dt = 0.01
g = 9.81
l = 1.0

kp = 20.0
kd = 6.0

# Standing sway
A_sway = 0.02
omega_sway = 1.0

# Walking
omega_gait = 2.0
alpha_walk = 0.7

bos_width = state.bos_right - state.bos_left

# --------------------------------------------------
# UI
# --------------------------------------------------
walk_mode = st.checkbox("Initiate Walk")

# --------------------------------------------------
# Time update
# --------------------------------------------------
st.session_state.t += dt

# --------------------------------------------------
# BOS centre
# --------------------------------------------------
x_center = (state.bos_left + state.bos_right) / 2

# --------------------------------------------------
# Gait phase update (only while walking)
# --------------------------------------------------
if walk_mode:
    state.gait_phase = update_gait_phase(
        state.gait_phase,
        omega_gait,
        dt
    )
else:
    state.gait_phase = 0.0

# --------------------------------------------------
# Reference selection
# --------------------------------------------------
if not walk_mode:
    # Normal standing with sway
    x_sway = A_sway * math.sin(omega_sway * st.session_state.t)
    x_ref = x_center + x_sway
else:
    # Walking: periodic bias then recenter
    if state.gait_phase < math.pi:
        x_ref = walk_reference(x_center, bos_width, alpha_walk)
    else:
        x_ref = x_center

# --------------------------------------------------
# Standing controller (always active)
# --------------------------------------------------
tau = standing_controller(
    state.x_com,
    state.x_com_dot,
    x_ref,
    kp,
    kd
)

# --------------------------------------------------
# Physics step (stance foot at BOS centre)
# --------------------------------------------------
state.x_com, state.x_com_dot = step_inverted_pendulum(
    state.x_com,
    state.x_com_dot,
    x_center,
    g,
    l,
    dt
)

# --------------------------------------------------
# Capture point
# --------------------------------------------------
x_cp = capture_point(state.x_com, state.x_com_dot, g, l)

# --------------------------------------------------
# Step trigger — CLOSE THE LOOP
# --------------------------------------------------
if walk_mode:
    if x_cp > state.bos_right or x_cp < state.bos_left:
        # Step distance = capture error
        step = x_cp - x_center

        # Move BOS forward
        state.bos_left += step
        state.bos_right += step

        # Swap stance foot (conceptual)
        state.stance_foot = "R" if state.stance_foot == "L" else "L"

        # Reset gait phase for next step
        state.gait_phase = 0.0

# --------------------------------------------------
# UI
# --------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("COM x", f"{state.x_com:.4f}")
col2.metric("COM velocity", f"{state.x_com_dot:.4f}")
col3.metric("Capture Point", f"{x_cp:.4f}")
col4.metric("Gait Phase", f"{state.gait_phase:.2f}")

st.write(
    f"BOS = [{state.bos_left:.3f}, {state.bos_right:.3f}] | "
    f"x_ref = {x_ref:.3f} | stance = {state.stance_foot}"
)

# --------------------------------------------------
# Save state
# --------------------------------------------------
st.session_state.state = state
