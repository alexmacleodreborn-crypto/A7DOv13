import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout="wide")
st.title("A7DOv13 — Full Anatomical Walker (Muscle-Driven)")

# --- Parameters ---
L_thigh = 0.12
L_shank = 0.12
L_foot = 0.08
L_torso = 0.18
head_radius = 0.03
I_thigh = 0.01
I_shank = 0.01
Fmax = 100
moment_arm = 0.04
ATP_max = 100.0

# --- State ---
if "gait_phase" not in st.session_state:
    st.session_state.gait_phase = 0.0
if "hip_angle" not in st.session_state:
    st.session_state.hip_angle = np.deg2rad(10)
if "knee_angle" not in st.session_state:
    st.session_state.knee_angle = np.deg2rad(20)
if "ankle_angle" not in st.session_state:
    st.session_state.ankle_angle = np.deg2rad(-5)
if "atp" not in st.session_state:
    st.session_state.atp = ATP_max

# --- Gait Controller ---
dt = 0.05
gait_speed = st.slider("Gait Speed", 1, 10, 4)
st.session_state.gait_phase += dt * gait_speed
if st.session_state.gait_phase > 2 * np.pi:
    st.session_state.gait_phase -= 2 * np.pi

# Target joint angles for walking (simple sine pattern)
hip_target = np.deg2rad(10) + np.deg2rad(20) * np.sin(st.session_state.gait_phase)
knee_target = np.deg2rad(20) + np.deg2rad(30) * np.sin(st.session_state.gait_phase + np.pi/2)
ankle_target = np.deg2rad(-5) + np.deg2rad(10) * np.sin(st.session_state.gait_phase + np.pi)

# --- Muscle Model ---
C_fatigue = st.session_state.atp / ATP_max
activation = 0.8  # For demo, fixed; in real model, set by controller

# Hip
F_hip_agon = Fmax * activation * C_fatigue
F_hip_ant = Fmax * (1 - activation) * C_fatigue
tau_hip = moment_arm * (F_hip_agon - F_hip_ant)
hip_accel = tau_hip / I_thigh
st.session_state.hip_angle += (hip_target - st.session_state.hip_angle) * 0.2 + hip_accel * dt

# Knee
F_knee_agon = Fmax * activation * C_fatigue
F_knee_ant = Fmax * (1 - activation) * C_fatigue
tau_knee = moment_arm * (F_knee_agon - F_knee_ant)
knee_accel = tau_knee / I_shank
st.session_state.knee_angle += (knee_target - st.session_state.knee_angle) * 0.2 + knee_accel * dt

# Ankle (simplified)
st.session_state.ankle_angle += (ankle_target - st.session_state.ankle_angle) * 0.2

# ATP drain
st.session_state.atp -= (abs(F_hip_agon) + abs(F_knee_agon)) * 0.0001
if st.session_state.atp < 0: st.session_state.atp = 0

# --- Forward Kinematics ---
hip_x, hip_y = 0.0, 0.08
knee_x = hip_x + L_thigh * np.sin(st.session_state.hip_angle)
knee_y = hip_y - L_thigh * np.cos(st.session_state.hip_angle)
ankle_x = knee_x + L_shank * np.sin(st.session_state.knee_angle)
ankle_y = knee_y - L_shank * np.cos(st.session_state.knee_angle)
foot_x = ankle_x + L_foot * np.sin(st.session_state.ankle_angle)
foot_y = ankle_y - L_foot * np.cos(st.session_state.ankle_angle)

# --- Visualisation ---
fig, ax = plt.subplots(figsize=(4, 3))
# Ground
ax.plot([-0.2, 0.2], [0, 0], 'k-', lw=2)
# Leg
ax.plot([hip_x, knee_x], [hip_y, knee_y], 'brown', lw=4, label='Thigh')
ax.plot([knee_x, ankle_x], [knee_y, ankle_y], 'brown', lw=4, label='Shank')
ax.plot([ankle_x, foot_x], [ankle_y, foot_y], 'brown', lw=4, label='Foot')
# Torso
ax.plot([hip_x, hip_x], [hip_y, hip_y + L_torso], 'g-', lw=6, label='Torso')
# Head
head_y = hip_y + L_torso + head_radius + 0.01
head = plt.Circle((hip_x, head_y), head_radius, color='orange', zorder=10)
ax.add_patch(head)
# Arms (simple)
shoulder_y = hip_y + L_torso
ax.plot([hip_x, hip_x - 0.07], [shoulder_y, shoulder_y + 0.08], 'purple', lw=4)
ax.plot([hip_x, hip_x + 0.07], [shoulder_y, shoulder_y + 0.08], 'purple', lw=4)
# Foot
ax.plot([foot_x], [foot_y], 'o', color='red', markersize=10, label='Foot')
ax.set_xlim(-0.2, 0.2)
ax.set_ylim(-0.05, head_y + head_radius + 0.05)
ax.axis('off')
ax.legend(loc='upper right', fontsize=8)
st.pyplot(fig)

st.markdown(f"""
ATP: {st.session_state.atp:.1f}  
Hip angle: {np.rad2deg(st.session_state.hip_angle):.1f}°  
Knee angle: {np.rad2deg(st.session_state.knee_angle):.1f}°  
Ankle angle: {np.rad2deg(st.session_state.ankle_angle):.1f}°  
Gait phase: {st.session_state.gait_phase:.2f}  
""")
