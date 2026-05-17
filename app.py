import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("A7DOv13 — Step-Based Walking (Knees & Hips Visualisation)")

# Persistent state
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

# Parameters
step_length = 0.15   # metres per step
com_advance = 0.08   # COM shift per step
torso_height = 0.18
head_radius = 0.03
shoulder_width = 0.08
arm_length = 0.12
hip_width = 0.06
leg_length = 0.15
knee_height = 0.05   # height of knee above foot

# UI
colA, colB = st.columns(2)
with colA:
    do_step = st.button("STEP")
with colB:
    reset = st.button("RESET")

# Reset logic
if reset:
    st.session_state.x_com = 0.0
    st.session_state.bos_left = -0.1
    st.session_state.bos_right = 0.1
    st.session_state.stance_foot = "L"
    st.session_state.step_count = 0

# Step logic
if do_step:
    st.session_state.x_com += com_advance
    if st.session_state.stance_foot == "L":
        st.session_state.bos_right = st.session_state.x_com + step_length / 2
        st.session_state.stance_foot = "R"
    else:
        st.session_state.bos_left = st.session_state.x_com - step_length / 2
        st.session_state.stance_foot = "L"
    st.session_state.x_com = (
        st.session_state.bos_left + st.session_state.bos_right
    ) / 2
    st.session_state.step_count += 1

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("COM x", f"{st.session_state.x_com:.3f}")
col2.metric("BOS Left", f"{st.session_state.bos_left:.3f}")
col3.metric("BOS Right", f"{st.session_state.bos_right:.3f}")
col4.metric("Steps", st.session_state.step_count)
st.write(f"Stance foot: {st.session_state.stance_foot}")

# Full Body Visualisation with Knees & Hips
fig, ax = plt.subplots(figsize=(4, 3))

# Draw ground
ax.plot([st.session_state.bos_left - 0.05, st.session_state.bos_right + 0.05], [0, 0], 'k-', lw=2)

# Draw feet
ax.plot([st.session_state.bos_left], [0], 'o', color='blue', markersize=10, label='Left Foot')
ax.plot([st.session_state.bos_right], [0], 'o', color='red', markersize=10, label='Right Foot')

# Calculate hip positions
hip_y = 0.08
hip_left = st.session_state.x_com - hip_width / 2
hip_right = st.session_state.x_com + hip_width / 2

# Draw hips
ax.plot([hip_left, hip_right], [hip_y, hip_y], 'c-', lw=6)

# Calculate knee positions
knee_left_x = (hip_left + st.session_state.bos_left) / 2
knee_right_x = (hip_right + st.session_state.bos_right) / 2
knee_left_y = knee_height
knee_right_y = knee_height

# Draw legs with knees
# Left leg: hip_left -> knee_left -> bos_left
ax.plot([hip_left, knee_left_x], [hip_y, knee_left_y], 'brown', lw=4)
ax.plot([knee_left_x, st.session_state.bos_left], [knee_left_y, 0], 'brown', lw=4)
# Right leg: hip_right -> knee_right -> bos_right
ax.plot([hip_right, knee_right_x], [hip_y, knee_right_y], 'brown', lw=4)
ax.plot([knee_right_x, st.session_state.bos_right], [knee_right_y, 0], 'brown', lw=4)

# Draw torso
torso_top_y = hip_y + torso_height
ax.plot([st.session_state.x_com, st.session_state.x_com], [hip_y, torso_top_y], 'g-', lw=6)

# Draw shoulders
shoulder_y = torso_top_y
shoulder_left = st.session_state.x_com - shoulder_width / 2
shoulder_right = st.session_state.x_com + shoulder_width / 2
ax.plot([shoulder_left, shoulder_right], [shoulder_y, shoulder_y], 'g-', lw=6)

# Draw arms
ax.plot([shoulder_left, shoulder_left], [shoulder_y, shoulder_y - arm_length], 'purple', lw=4)
ax.plot([shoulder_right, shoulder_right], [shoulder_y, shoulder_y - arm_length], 'purple', lw=4)

# Draw head
head_y = shoulder_y + head_radius + 0.01
head = plt.Circle((st.session_state.x_com, head_y), head_radius, color='orange', zorder=10)
ax.add_patch(head)

# Highlight stance foot
if st.session_state.stance_foot == "L":
    ax.plot([st.session_state.bos_left], [0], 'o', color='lime', markersize=14, label='Stance')
else:
    ax.plot([st.session_state.bos_right], [0], 'o', color='lime', markersize=14, label='Stance')

ax.set_xlim(st.session_state.bos_left - 0.2, st.session_state.bos_right + 0.2)
ax.set_ylim(-0.05, head_y + head_radius + 0.05)
ax.axis('off')
ax.legend(loc='upper right', fontsize=8)

st.pyplot(fig)

st.markdown("""
### What you should see

- Every click on STEP moves the full body forward
- Feet alternate left/right
- Knees and hips are shown in the stick figure
- COM always stays between feet
- Stick figure shows legs, knees, hips, torso, arms, head, stance
- Motion is obvious and visible

This is intentional. We are validating walking structure and full body geometry, not continuous physics.
""")
