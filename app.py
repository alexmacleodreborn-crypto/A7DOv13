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
st.title("A7DOv13 — Standing & Walking (Correct Support Logic)")

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

kp = 25.0
kd = 7.0

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
# BOS
# --------------------------------------------------
bos_left = state.bos_left
bos_right = state.bos_right
x_center = (bos_left + bos_right) / 2
bos_width = bos_right - bos_left

# --------------------------------------------------
# SUPPORT MODE (CRITICAL)
# --------------------------------------------------
if walk_mode:
    support_mode = "single"
else:
    support_mode = "double"

# --------------------------------------------------
# GAIT PHASE
# --------------------------------------------------
if walk_mode:
    state.gait_phase = update_gait_phase(
        state.gait_phase,
        omega_gait,
        dt
    )
else:
    # FULL RESET when not walking
    state.gait_phase = 0.0
    state.stance_foot = "L"

# --------------------------------------------------
# CONTROLLER REFERENCE
# --------------------------------------------------
if not walk_mode:
    # PURE STANDING
    x_sway = A_sway * math.sin(omega_sway * st.session_state.t)
    x_ref = x_center + x_sway
else:
    # WALKING: bias only in early gait
    if state.gait_phase < math.pi:
        x_ref = walk_reference(x_center, bos_width, alpha_walk)
    else:
        x_ref = x_center

# --------------------------------------------------
# STANDING CONTROLLER
# --------------------------------------------------
tau = standing_controller(
    state.x_com,
    state.x_com_dot,
    x_ref,
    kp,
    kd
)

# --------------------------------------------------
# PHYSICS SUPPORT POINT (THE FIX)
# --------------------------------------------------
if support_mode == "double":
    # BOTH FEET → SUPPORT AT BOS CENTRE
    x_support = x_center
else:
    # SINGLE FOOT SUPPORT
    if state.stance_foot == "L":
        x_support = bos_left
    else:
        x_support = bos_right

# --------------------------------------------------
# PHYSICS STEP
# --------------------------------------------------
state.x_com, state.x_com_dot = step_inverted_pendulum(
    state.x_com,
    state.x_com_dot,
    x_support,
    g,
    l,
    dt
)

# --------------------------------------------------
# CAPTURE POINT
# --------------------------------------------------
x_cp = capture_point(state.x_com, state.x_com_dot, g, l)

# --------------------------------------------------
# STEP TRIGGER (ONLY IN WALK MODE)
# --------------------------------------------------
if walk_mode and support_mode == "single":
    if x_cp > bos_right or x_cp < bos_left:
        step_location = x_cp

        if state.stance_foot == "L":
            state.bos_right = step_location
            state.stance_foot = "R"
        else:
            state.bos_left = step_location
            state.stance_foot = "L"

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
    f"Mode: {support_mode} | "
    f"BOS = [{state.bos_left:.3f}, {state.bos_right:.3f}] | "
    f"Support @ {x_support:.3f} | "
    f"Stance = {state.stance_foot}"
)

# --------------------------------------------------
# SAVE STATE
# --------------------------------------------------
st.session_state.state = state
