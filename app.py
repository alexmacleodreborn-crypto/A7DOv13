import math
import streamlit as st

from a7do.state import A7DOState
from a7do.control.standing import standing_controller
from a7do.control.recovery import capture_point
from a7do.control.walk_init import walk_reference
from a7do.control.gait import update_gait_phase

# ==================================================
# Streamlit setup
# ==================================================
st.set_page_config(layout="wide")
st.title("A7DOv13 — Standing & Walking (Final Correct Model)")

# ==================================================
# Initialise persistent state
# ==================================================
if "state" not in st.session_state:
    st.session_state.state = A7DOState()

if "t" not in st.session_state:
    st.session_state.t = 0.0

if "support_phase" not in st.session_state:
    st.session_state.support_phase = "double"   # 'double' or 'single'

if "ds_timer" not in st.session_state:
    st.session_state.ds_timer = 0.0

state = st.session_state.state

# ==================================================
# Parameters
# ==================================================
dt = 0.01
g = 9.81
l = 1.0
m = 1.0

# Standing control
kp = 25.0
kd = 7.0

# Natural sway (standing only)
A_sway = 0.02
omega_sway = 1.0

# Walking
omega_gait = 2.0
alpha_walk = 0.7
double_support_duration = 0.15
impact_damping = 0.25
initiation_velocity = 0.05   # ✅ walk intent impulse

# ==================================================
# UI
# ==================================================
walk_mode = st.checkbox("Initiate Walk")

# ==================================================
# Time update
# ==================================================
st.session_state.t += dt

# ==================================================
# BOS
# ==================================================
bos_left = state.bos_left
bos_right = state.bos_right
x_center = (bos_left + bos_right) / 2
bos_width = bos_right - bos_left

# ==================================================
# GAIT PHASE
# ==================================================
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

# ==================================================
# SUPPORT PHASE TRANSITIONS
# ==================================================
if st.session_state.support_phase == "double":
    st.session_state.ds_timer += dt
    if walk_mode and st.session_state.ds_timer >= double_support_duration:
        # Enter single support with intent
        st.session_state.support_phase = "single"
        st.session_state.ds_timer = 0.0

        # ✅ CRITICAL: walk initiation impulse
        state.x_com_dot = initiation_velocity

# ==================================================
# CONTROLLER REFERENCE
# ==================================================
if not walk_mode:
    # Standing sway
    x_sway = A_sway * math.sin(omega_sway * st.session_state.t)
    x_ref = x_center + x_sway
else:
    # Walking lean only during early single support
    if st.session_state.support_phase == "single" and state.gait_phase < math.pi:
        x_ref = walk_reference(x_center, bos_width, alpha_walk)
    else:
        x_ref = x_center

# ==================================================
# CONTROLLER (used only for standing / lean shaping)
# ==================================================
tau = standing_controller(
    state.x_com,
    state.x_com_dot,
    x_ref,
    kp,
    kd
)

# ==================================================
# PHYSICS UPDATE
# ==================================================
if st.session_state.support_phase == "double":
    # ✅ Double support = kinematic constraint
    state.x_com = x_center
    state.x_com_dot = 0.0

else:
    # ✅ Single support = pure inverted pendulum
    x_support = bos_left if state.stance_foot == "L" else bos_right
    x_ddot = (g / l) * (state.x_com - x_support)
    state.x_com_dot += x_ddot * dt
    state.x_com += state.x_com_dot * dt

# ==================================================
# CAPTURE POINT
# ==================================================
x_cp = capture_point(state.x_com, state.x_com_dot, g, l)

# ==================================================
# STEP EVENT (end of single support)
# ==================================================
if walk_mode and st.session_state.support_phase == "single":
    if x_cp > bos_right or x_cp < bos_left:
        step_location = x_cp

        if state.stance_foot == "L":
            state.bos_right = step_location
            state.stance_foot = "R"
        else:
            state.bos_left = step_location
            state.stance_foot = "L"

        # Impact: lose momentum
        state.x_com_dot *= impact_damping

        # Enter double support
        st.session_state.support_phase = "double"
        st.session_state.ds_timer = 0.0
        state.gait_phase = 0.0

# ==================================================
# UI DISPLAY
# ==================================================
gait_norm = state.gait_phase / (2 * math.pi)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("COM x", f"{state.x_com:.6f}")
col2.metric("COM velocity", f"{state.x_com_dot:.6f}")
col3.metric("Capture Point", f"{x_cp:.6f}")
col4.metric("Gait Phase (0–1)", f"{gait_norm:.2f}")
col5.metric("Support", st.session_state.support_phase)

st.write(
    f"BOS = [{state.bos_left:.3f}, {state.bos_right:.3f}] | "
    f"Support @ {'centre' if st.session_state.support_phase=='double' else state.stance_foot} | "
    f"Stance = {state.stance_foot}"
)

# ==================================================
# SAVE STATE
# ==================================================
st.session_state.state = state
