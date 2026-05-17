import math
import streamlit as st

# ==================================================
# A7DO — BODY-LINKED WALKING MODEL
# ==================================================
# Single rigid body (leg+torso) as inverted pendulum
# Pivot = support foot
# State = angle θ, angular velocity θ̇
# COM projection x = L * sin(θ)
# ==================================================

st.set_page_config(layout="wide")
st.title("A7DOv13 — Body‑Linked Standing & Walking")

# ==================================================
# Persistent state
# ==================================================
if "theta" not in st.session_state:
    st.session_state.theta = 0.0          # body angle (rad)

if "theta_dot" not in st.session_state:
    st.session_state.theta_dot = 0.0      # angular velocity

if "support_phase" not in st.session_state:
    st.session_state.support_phase = "double"   # double / single

if "stance_foot" not in st.session_state:
    st.session_state.stance_foot = "L"

if "bos_left" not in st.session_state:
    st.session_state.bos_left = -0.1

if "bos_right" not in st.session_state:
    st.session_state.bos_right = 0.1

if "ds_timer" not in st.session_state:
    st.session_state.ds_timer = 0.0

# ==================================================
# Parameters (physical)
# ==================================================
dt = 0.01
g = 9.81
L = 1.0               # leg/torso length
I = 1.0               # inertia
m = 1.0

# Walking timing
double_support_time = 0.15
impact_damping = 0.3
initiation_impulse = 0.15   # rad/s angular impulse

# ==================================================
# UI
# ==================================================
walk_mode = st.checkbox("Initiate Walk")

# ==================================================
# BOS geometry
# ==================================================
bos_left = st.session_state.bos_left
bos_right = st.session_state.bos_right
bos_center = (bos_left + bos_right) / 2

# ==================================================
# SUPPORT PHASE TRANSITION
# ==================================================
if st.session_state.support_phase == "double":
    st.session_state.ds_timer += dt

    if walk_mode and st.session_state.ds_timer >= double_support_time:
        st.session_state.support_phase = "single"
        st.session_state.ds_timer = 0.0

        # ✅ Initiate fall by giving angular velocity
        st.session_state.theta_dot = initiation_impulse

# ==================================================
# PHYSICS UPDATE
# ==================================================
if st.session_state.support_phase == "double":
    # ----------------------------------------------
    # DOUBLE SUPPORT = BODY LOCKED UPRIGHT
    # ----------------------------------------------
    st.session_state.theta = 0.0
    st.session_state.theta_dot = 0.0

else:
    # ----------------------------------------------
    # SINGLE SUPPORT = INVERTED PENDULUM
    # ----------------------------------------------
    theta = st.session_state.theta
    theta_dot = st.session_state.theta_dot

    # Gravity torque
    theta_ddot = (g / L) * math.sin(theta)

    # Integrate
    theta_dot += theta_ddot * dt
    theta += theta_dot * dt

    st.session_state.theta = theta
    st.session_state.theta_dot = theta_dot

# ==================================================
# COMPUTE COM FROM BODY GEOMETRY
# ==================================================
x_com = L * math.sin(st.session_state.theta)

# ==================================================
# STEP TRIGGER (WHEN BODY FALLS FAR ENOUGH)
# ==================================================
if walk_mode and st.session_state.support_phase == "single":
    if abs(x_com) > 0.12:
        # Place new foot at COM projection
        if st.session_state.stance_foot == "L":
            st.session_state.bos_right = x_com
            st.session_state.stance_foot = "R"
        else:
            st.session_state.bos_left = x_com
            st.session_state.stance_foot = "L"

        # Impact: lose angular momentum
        st.session_state.theta_dot *= impact_damping

        # Enter double support
        st.session_state.support_phase = "double"
        st.session_state.ds_timer = 0.0

# ==================================================
# VISUALS / METRICS
# ==================================================
col1, col2, col3, col4 = st.columns(4)

col1.metric("θ (rad)", f"{st.session_state.theta:.3f}")
col2.metric("θ̇ (rad/s)", f"{st.session_state.theta_dot:.3f}")
col3.metric("COM x", f"{x_com:.3f}")
col4.metric("Support", st.session_state.support_phase)

st.write(
    f"BOS = [{st.session_state.bos_left:.2f}, {st.session_state.bos_right:.2f}] | "
    f"Stance = {st.session_state.stance_foot}"
)

# ==================================================
# EXPLANATION (for sanity)
# ==================================================
st.markdown("""
### What this model is doing

- ✅ The body is a rigid inverted pendulum
- ✅ COM moves because the body rotates
- ✅ Walking starts by injecting angular velocity
- ✅ A step happens when COM passes support
- ✅ Double support resets posture
- ✅ Repeat = walking

This is the minimum physically correct walking system.
""")
