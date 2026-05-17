import streamlit as st
from a7do.state import A7DOState
from a7do.physics.inverted_pendulum import step_inverted_pendulum
from a7do.control.standing import standing_controller
from a7do.control.recovery import capture_point

st.set_page_config(layout="wide")
st.title("A7DOv13 — Developmental Organism")

# Initialise state
if "state" not in st.session_state:
    st.session_state.state = A7DOState()

state = st.session_state.state

# Parameters
dt = 0.01
g = 9.81
l = 1.0
kp = 20.0
kd = 6.0

# Standing reference (centre of BOS)
x_ref = (state.bos_left + state.bos_right) / 2

# Standing control
tau = standing_controller(
    state.x_com,
    state.x_com_dot,
    x_ref,
    kp,
    kd
)

# Physics step
state.x_com, state.x_com_dot = step_inverted_pendulum(
    state.x_com,
    state.x_com_dot,
    x_ref,
    g,
    l,
    dt
)

# Capture point
x_cp = capture_point(state.x_com, state.x_com_dot, g, l)

# UI
col1, col2, col3 = st.columns(3)
col1.metric("COM x", f"{state.x_com:.4f}")
col2.metric("COM velocity", f"{state.x_com_dot:.4f}")
col3.metric("Capture Point", f"{x_cp:.4f}")

st.progress(min(1.0, state.atp / state.atp_max))

st.session_state.state = state
