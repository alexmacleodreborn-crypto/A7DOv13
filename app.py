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
st.title("A7DOv13 — Standing → Walking")

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

bos_width = state.bos_right - state.bos_left

# Gait parameters
omega_gait = 2.0          # rad/s
step_threshold = 0.9      # capture-point exit ratio

# --------------------------------------------------
# UI controls
# --------------------------------------------------
walk_mode = st.checkbox("Initiate Walk")

# --------------------------------------------------
# Time update
# --------------------------------------------------
st.session_state.t += dt

# --------------------------------------------------
# Standing reference
# --------------------------------------------------
x_center = (state.bos_left + state.bos_right) / 2
x_sway = A_sway * math.sin(omega_sway * st.session_state.t)
x_ref = x_center + x_sway

# --------------------------------------------------
# Walk initiation bias
# --------------------------------------------------
if walk_mode:
    x_ref = walk_reference(x_center, bos_width)

# --------------------------------------------------
# Standing control
# --------------------------------------------------
tau = standing_controller(
    state.x_com,
    state.x_com_dot,
    x_ref,
    kp,
    kd
)

# --------------------------------------------------
# Physics step (stance foot assumed at x_ref)
# --------------------------------------------------
state.x_com, state.x_com_dot = step_inverted_pendulum(
    state.x_com,
    state.x_com_dot,
    x_ref,
    g,
    l,
    dt
)

# --------------------------------------------------
# Capture point
# --------------------------------------------------
x_cp = capture_point(state.x_com, state.x_com_dot, g, l)

# --------------------------------------------------
# Step trigger (capture exits BOS)
# --------------------------------------------------
if walk_mode and abs(x_cp - x_center) > step_threshold * bos_width:
    # Take a step: move BOS forward
    step = x_cp - x_center
    state.bos_left += step
    state.bos_right += step

    # Reset gait phase
    state.gait_phase = 0.0

# --------------------------------------------------
# Gait phase update (after first step)
# --------------------------------------------------
if walk_mode:
    state.gait_phase = update_gait_phase(
        state.gait_phase,
        omega_gait,
        dt
    )

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
    f"x_ref = {x_ref:.3f}"
)

# Save state
st.session_state.state = state
