import math
import streamlit as st

from a7do.state import A7DOState
from a7do.physics.inverted_pendulum import step_inverted_pendulum
from a7do.control.standing import standing_controller
from a7do.control.recovery import capture_point

# --------------------------------------------------
# Streamlit setup
# --------------------------------------------------
st.set_page_config(layout="wide")
st.title("A7DOv13 — Developmental Organism (Standing)")

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

# Natural sway parameters
A_sway = 0.02        # 2 cm
omega_sway = 1.0    # 1 Hz

# --------------------------------------------------
# Time update
# --------------------------------------------------
st.session_state.t += dt

# --------------------------------------------------
# Reference position (standing + sway)
# --------------------------------------------------
x_center = (state.bos_left + state.bos_right) / 2
x_sway = A_sway * math.sin(omega_sway * st.session_state.t)
x_ref = x_center + x_sway

# --------------------------------------------------
# External disturbance (debug / testing)
# --------------------------------------------------
push = st.slider("External Push", -0.3, 0.3, 0.0)
state.x_com += push * dt

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
# Physics step
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
# UI
# --------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("COM x", f"{state.x_com:.4f}")
col2.metric("COM velocity", f"{state.x_com_dot:.4f}")
col3.metric("Capture Point", f"{x_cp:.4f}")
col4.metric("ATP", f"{state.atp:.1f}")

# Visual BOS indicator
st.write(
    f"BOS = [{state.bos_left:.2f}, {state.bos_right:.2f}] | "
    f"x_ref = {x_ref:.3f}"
)

# Store state
st.session_state.state = state
