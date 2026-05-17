import streamlit as st

# ==================================================
# A7DO — STEP-BASED WALKING (VISIBLE & DEBUGGABLE)
# ==================================================

st.set_page_config(layout="wide")
st.title("A7DOv13 — Step-Based Walking (Correct for Streamlit)")

# ==================================================
# Persistent state
# ==================================================
if "x_com" not in st.session_state:
    st.session_state.x_com = 0.0

if "bos_left" not in st.session_state:
    st.session_state.bos_left = -0.1

if "bos_right" not in st.session_state:
    st.session_state.bos_right = 0.1

if "stance_foot" not in st.session_state:
    st.session_state.stance_foot = "L"

if "step_count" not in st.session_state:
    st.session_state.step_count = 0

# ==================================================
# Parameters
# ==================================================
step_length = 0.15   # metres per step
com_advance = 0.08   # COM shift per step

# ==================================================
# UI
# ==================================================
colA, colB = st.columns(2)

with colA:
    do_step = st.button("STEP")

with colB:
    reset = st.button("RESET")

# ==================================================
# Reset logic
# ==================================================
if reset:
    st.session_state.x_com = 0.0
    st.session_state.bos_left = -0.1
    st.session_state.bos_right = 0.1
    st.session_state.stance_foot = "L"
    st.session_state.step_count = 0

# ==================================================
# Step logic (THIS CREATES MOTION)
# ==================================================
if do_step:
    # 1. Move COM forward
    st.session_state.x_com += com_advance

    # 2. Place swing foot
    if st.session_state.stance_foot == "L":
        st.session_state.bos_right = st.session_state.x_com + step_length / 2
        st.session_state.stance_foot = "R"
    else:
        st.session_state.bos_left = st.session_state.x_com - step_length / 2
        st.session_state.stance_foot = "L"

    # 3. Re-centre COM between feet
    st.session_state.x_com = (
        st.session_state.bos_left + st.session_state.bos_right
    ) / 2

    st.session_state.step_count += 1

# ==================================================
# UI OUTPUT
# ==================================================
col1, col2, col3, col4 = st.columns(4)

col1.metric("COM x", f"{st.session_state.x_com:.3f}")
col2.metric("BOS Left", f"{st.session_state.bos_left:.3f}")
col3.metric("BOS Right", f"{st.session_state.bos_right:.3f}")
col4.metric("Steps", st.session_state.step_count)

st.write(
    f"Stance foot: {st.session_state.stance_foot}"
)

st.markdown("""
### What you should see

- Every click on STEP moves the body forward
- Feet alternate left/right
- COM always stays between feet
- Motion is obvious and visible

This is intentional.
We are validating walking structure, not continuous physics.
""")
