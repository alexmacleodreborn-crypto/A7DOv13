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
st.title("A7DOv13 — Standing → Walking (Corrected Physics)")

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

A_sway = 0.02
omega_sway = 1.0

omega_gait = 2.0
alpha_walk = 0.7

# --------------------------------------------------
# UI
# --------------------------------------------------
walk_mode = st.checkbox("Initiate Walk")

# --------------------------------------------------
# Time update
# --------------------------------------------------
st.session_state.t += dt

# --------------------------------------------------
# Current BOS and stance foot
# --------------------------------------------------
bos_left = state.bos_left
bos_right = state.bos_right
x_center = (bos_left + bos_right) / 2

# Define stance foot position
if state.stance_foot == "L":
    x_foot = bos_left
else:
    x_foot = bos_right

bos_width = bos_right - bos_left

# --------------------------------------------------
# Gait phase
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
# Reference (what controller wants)
# --------------------------------------------------
if not walk_mode:
    x_sway = A_sway * math.sin(omega_sway * st.session_state.t)
    x_ref = x_center + x_sway
else:
    # Lean only during first half of gait
    if state.gait_phase < math.pi:
        x_ref = walk_reference(x_center, bos_width, alpha_walk)
    else:
        x_ref = x_center

# --------------------------------------------------
# Standing controller (always)
# --------------------------------------------------
tau = standing_controller(
    state.x_com,
    state.x_com_dot,
    x_ref,
    kp,
    kd
)

# --------------------------------------------------
# PHYSICS — THIS IS THE CRITICAL FIX
# --------------------------------------------------
state.x_com, state.x_com_dot = step_inverted_pendulum(
    state.x_com,
    state.x_com_dot,
    x_foot,     # ✅ USE STANCE FOOT
    g,
    l,
    dt
)

# --------------------------------------------------
# Capture point
# --------------------------------------------------
x_cp = capture_point(state.x_com, state.x_com_dot, g, l)

# --------------------------------------------------
# STEP TRIGGER (capture exits BOS)
# --------------------------------------------------
if walk_mode:
    if x_cp > bos_right or x_cp < bos_left:
        # Place new foot at capture point
        step_location = x_cp

        if state.stance_foot == "L":
            state.bos_right = step_location
            state.stance_foot = "R"
        else:
            state.bos_left = step_location
            state.stance_foot = "L"

        # Reset gait phase
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
    f"stance = {state.stance_foot} | x_ref = {x_ref:.3f}"
)

# --------------------------------------------------
# Save state
# --------------------------------------------------
st.session_state.state = state
