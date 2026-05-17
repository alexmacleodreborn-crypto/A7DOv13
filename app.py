import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout="wide")
st.title("A7DOv13 — Step-Based Anatomical Walker (with Arm Motion)")

# --- Parameters ---
L_thigh = 0.12
L_shank = 0.12
L_foot = 0.08
L_torso = 0.18
head_radius = 0.03
L_upperarm = 0.10
L_forearm = 0.10
shoulder_width = 0.10

# --- State ---
if "gait_phase" not in st.session_state:
    st.session_state.gait_phase = 0
if "step_count" not in st.session_state:
    st.session_state.step_count = 0

# --- Step Button ---
do_step = st.button("STEP")
reset = st.button("RESET")

if reset:
    st.session_state.gait_phase = 0
    st.session_state.step_count = 0

if do_step:
    st.session_state.gait_phase += 1
    st.session_state.step_count += 1

# --- Gait Logic: Step-based, alternating legs ---
phase = st.session_state.gait_phase % 2
# Left stance, right swing (phase 0); Right stance, left swing (phase 1)

# Joint angles for each leg (simple realistic pattern)
hip_angle_L = np.deg2rad(10) if phase == 0 else np.deg2rad(30)
knee_angle_L = np.deg2rad(20) if phase == 0 else np.deg2rad(60)
ankle_angle_L = np.deg2rad(-5) if phase == 0 else np.deg2rad(10)

hip_angle_R = np.deg2rad(30) if phase == 0 else np.deg2rad(10)
knee_angle_R = np.deg2rad(60) if phase == 0 else np.deg2rad(20)
ankle_angle_R = np.deg2rad(10) if phase == 0 else np.deg2rad(-5)

# --- Arm swing: opposite to legs ---
# Shoulder angles: swing amplitude 30 deg
shoulder_angle_L = np.deg2rad(-30) if phase == 0 else np.deg2rad(30)
shoulder_angle_R = np.deg2rad(30) if phase == 0 else np.deg2rad(-30)
elbow_angle_L = np.deg2rad(20)
elbow_angle_R = np.deg2rad(20)

# --- Forward Kinematics ---
hip_x, hip_y = 0.0, 0.08
# Shoulders
shoulder_y = hip_y + L_torso
shoulder_left_x = hip_x - shoulder_width / 2
shoulder_right_x = hip_x + shoulder_width / 2

# Left leg
knee_x_L = hip_x - L_thigh * np.sin(hip_angle_L)
knee_y_L = hip_y - L_thigh * np.cos(hip_angle_L)
ankle_x_L = knee_x_L - L_shank * np.sin(knee_angle_L)
ankle_y_L = knee_y_L - L_shank * np.cos(knee_angle_L)
foot_x_L = ankle_x_L - L_foot * np.sin(ankle_angle_L)
foot_y_L = ankle_y_L - L_foot * np.cos(ankle_angle_L)
# Right leg
knee_x_R = hip_x + L_thigh * np.sin(hip_angle_R)
knee_y_R = hip_y - L_thigh * np.cos(hip_angle_R)
ankle_x_R = knee_x_R + L_shank * np.sin(knee_angle_R)
ankle_y_R = knee_y_R - L_shank * np.cos(knee_angle_R)
foot_x_R = ankle_x_R + L_foot * np.sin(ankle_angle_R)
foot_y_R = ankle_y_R - L_foot * np.cos(ankle_angle_R)

# Left arm
elbow_x_L = shoulder_left_x + L_upperarm * np.sin(shoulder_angle_L)
elbow_y_L = shoulder_y - L_upperarm * np.cos(shoulder_angle_L)
wrist_x_L = elbow_x_L + L_forearm * np.sin(shoulder_angle_L + elbow_angle_L)
wrist_y_L = elbow_y_L - L_forearm * np.cos(shoulder_angle_L + elbow_angle_L)
# Right arm
elbow_x_R = shoulder_right_x + L_upperarm * np.sin(shoulder_angle_R)
elbow_y_R = shoulder_y - L_upperarm * np.cos(shoulder_angle_R)
wrist_x_R = elbow_x_R + L_forearm * np.sin(shoulder_angle_R + elbow_angle_R)
wrist_y_R = elbow_y_R - L_forearm * np.cos(shoulder_angle_R + elbow_angle_R)

# --- Visualisation ---
fig, ax = plt.subplots(figsize=(4, 3))
# Ground
ax.plot([-0.2, 0.2], [0, 0], 'k-', lw=2)
# Left leg
ax.plot([hip_x, knee_x_L], [hip_y, knee_y_L], 'brown', lw=4)
ax.plot([knee_x_L, ankle_x_L], [knee_y_L, ankle_y_L], 'brown', lw=4)
ax.plot([ankle_x_L, foot_x_L], [ankle_y_L, foot_y_L], 'brown', lw=4)
# Right leg
ax.plot([hip_x, knee_x_R], [hip_y, knee_y_R], 'blue', lw=4)
ax.plot([knee_x_R, ankle_x_R], [knee_y_R, ankle_y_R], 'blue', lw=4)
ax.plot([ankle_x_R, foot_x_R], [ankle_y_R, foot_y_R], 'blue', lw=4)
# Torso
ax.plot([hip_x, hip_x], [hip_y, shoulder_y], 'g-', lw=6)
# Shoulders
ax.plot([shoulder_left_x, shoulder_right_x], [shoulder_y, shoulder_y], 'g-', lw=6)
# Head
head_y = shoulder_y + head_radius + 0.01
head = plt.Circle((hip_x, head_y), head_radius, color='orange', zorder=10)
ax.add_patch(head)
# Left arm
ax.plot([shoulder_left_x, elbow_x_L], [shoulder_y, elbow_y_L], 'purple', lw=4)
ax.plot([elbow_x_L, wrist_x_L], [elbow_y_L, wrist_y_L], 'purple', lw=4)
# Right arm
ax.plot([shoulder_right_x, elbow_x_R], [shoulder_y, elbow_y_R], 'purple', lw=4)
ax.plot([elbow_x_R, wrist_x_R], [elbow_y_R, wrist_y_R], 'purple', lw=4)
# Feet
ax.plot([foot_x_L], [foot_y_L], 'o', color='red', markersize=10)
ax.plot([foot_x_R], [foot_y_R], 'o', color='blue', markersize=10)
ax.set_xlim(-0.2, 0.2)
ax.set_ylim(-0.05, head_y + head_radius + 0.05)
ax.axis('off')
st.pyplot(fig)

st.markdown(f"""
Step count: {st.session_state.step_count}  
Gait phase: {st.session_state.gait_phase % 2}  
Stance: {"Left" if phase == 0 else "Right"}  
Arms swing opposite to legs
""")
