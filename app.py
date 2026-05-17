import math
import streamlit as st

from a7do.state import A7DOState
from a7do.control.standing import standing_controller
from a7do.control.recovery import capture_point
from a7do.control.walk_init import walk_reference
from a7do.control.gait import update_gait_phase

# --------------------------------------------------
# Streamlit setup
# --------------------------------------------------
st.set_page_config(layout="wide")
st.title("A7DOv13 — Standing → Walking (Double Support Correct)")

# --------------------------------------------------
# Initialise state
# --------------------------------------------------
if "state" not in st.session_state:
    st.session_state.state = A7DOState()

if "t" not in st.session_state:
    st.session_state.t = 0.0

if "support_phase" not in st.session_state:
    st.session_state.support_phase = "double"   # 'double' or 'single'

if "ds_timer" not in st.session_state:
    st.session_state.ds_timer = 0.0              # double support timer

state = st.session_state.state

# --------------------------------------------------
# Parameters
# --------------------------------------------------
dt = 0.01
g = 9.81
l = 1.0
m = 1.0

kp = 25.0
kd = 7.0

A_sway = 0.02
omega_sway = 1.0

omega_gait = 2.0
alpha_walk = 0.7

double_support_duration = 0.15   # seconds
impact_damping = 0.25            # velocity loss on landing

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
# GAIT PHASE
# --------------------------------------------------
if walk_mode:
    state.gait_phase = update_gait_phase(
        state.gait_phase,
        omega_gait,
        dt
    )
else:
    state.gait_phase = 0.0
    state.stance_foot = "L"
    st.session_state.support_phase = "double"
    st.session_state.ds_timer = 0.0

# --------------------------------------------------
# SUPPORT PHASE LOGIC (THE KEY FIX)
# --------------------------------------------------
if st.session_state.support_phase == "double":
    st.session_state.ds_timer += dt
    if st.session_state.ds_timer >= double_support_duration and walk_mode:
        st.session_state.support_phase = "single"
        st.session_state.ds_timer = 0.0

# --------------------------------------------------
# CONTROLLER REFERENCE
# --------------------------------------------------
if not walk_mode:
    # Pure standing
    x_sway = A_sway * math.sin(omega_sway * st.session_state.t)
    x_ref = x_center + x_sway
else:
    if st.session_state.support_phase == "single" and state.gait_phase < math.pi:
        x_ref = walk_reference(x_center, bos_width, alpha_walk)
    else:
        x_ref = x_center

# --------------------------------------------------
# CONTROLLER
# --------------------------------------------------
tau = standing_controller(
    state.x_com,
    state.x_com_dot,
    x_ref,
    kp,
    kd
)

# --------------------------------------------------
# PHYSICS SUPPORT POINT
# --------------------------------------------------
if st.session_state.support_phase == "double":
    x_support = x_center
else:
    x_support = bos_left if state.stance_foot == "L" else bos_right

# --------------------------------------------------
# CONTROLLED INVERTED PENDULUM
# --------------------------------------------------
x_ddot = (g / l) * (state.x_com - x_support) + tau / (m * l)
state.x_com_dot += x_ddot * dt
state.x_com += state.x_com_dot * dt

# --------------------------------------------------
# CAPTURE POINT
# --------------------------------------------------
x_cp = capture_point(state.x_com, state.x_com_dot, g, l)

# --------------------------------------------------
# STEP EVENT (END OF SINGLE SUPPORT)
# --------------------------------------------------
if walk_mode and st.session_state.support_phase == "single":
    if x_cp > bos_right or x_cp < bos_left:
        step_location = x_cp

        if state.stance_foot == "L":
            state.bos_right = step_location
            state.stance_foot = "R"
        else:
            state.bos_left = step_location
            state.stance_foot = "L"

        # Impact dynamics
        state.x_com_dot *= impact_damping

        # Enter double support
        st.session_state.support_phase = "double"
        st.session_state.ds_timer = 0.0
        state.gait_phase = 0.0

# --------------------------------------------------
# UI
# --------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("COM x", f"{state.x_com:.5f}")
col2.metric("COM velocity", f"{state.x_com_dot:.5f}")
col3.metric("Capture Point", f"{x_cp:.5f}")
col4.metric("Gait Phase", f"{state.gait_phase:.2f}")
col5.metric("Support", st.session_state.support_phase)

st.write(
    f"BOS = [{state.bos_left:.3f}, {state.bos_right:.3f}] | "
    f"Support @ {x_support:.3f} | "
    f"Stance = {state.stance_foot}"
)

# --------------------------------------------------
# SAVE STATE
# --------------------------------------------------
st.session_state.state = state
