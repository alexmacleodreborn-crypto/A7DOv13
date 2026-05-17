import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout="wide")
st.title("A7DOv13 — Anatomical Two-Legged Walker (Muscle-Driven)")

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
if "hip_angle_L" not in st.session_state:
    st.session_state.hip_angle_L = np.deg2rad(10)
if "knee_angle_L" not in st.session_state:
    st.session_state.knee_angle_L = np.deg2rad(20)
if "ankle_angle_L" not in st.session_state:
    st.session_state.ankle_angle_L = np.deg2rad(-5)
if "hip_angle_R" not in st.session_state:
    st.session_state.hip_angle_R = np.deg2rad(10)
if "knee_angle_R" not in st.session_state:
    st.session_state.knee_angle_R = np.deg2rad(20)
if "ankle_angle_R" not in st.session_state:
    st.session_state.ankle_angle_R = np.deg2rad(-5)
if "atp" not in st.session_state:
    st.session_state.atp = ATP_max

# --- Gait Controller ---
dt = 0.05
gait_speed = st.slider("Gait Speed", 1, 10, 4)
st.session_state.gait_phase += dt * gait_speed
if st.session_state.gait_phase > 2 * np.pi:
    st.session_state.gait_phase -= 2 * np.pi

# Target joint angles for walking (alternating legs)
hip_target_L = np.deg2rad(10) + np.deg2rad(20) * np.sin(st.session_state.gait_phase)
knee_target_L = np.deg2rad(20) + np.deg2rad(30) * np.sin(st.session_state.gait_phase + np.pi/2)
ankle_target_L = np.deg2rad(-5) + np.deg2rad(10) * np.sin(st.session_state.gait_phase + np.pi)

hip_target_R = np.deg2rad(10) + np.deg2rad(20) * np.sin(st.session_state.gait_phase + np.pi)
knee_target_R = np.deg2rad(20) + np.deg2rad(30) * np.sin(st.session_state.gait_phase + np.pi/2 + np.pi)
ankle_target_R = np.deg2rad(-5) + np.deg2rad(10) * np.sin(st.session_state.gait_phase + np.pi + np.pi)

# --- Muscle Model ---
C_fatigue = st.session_state.atp / ATP_max
activation = 0.8  # For demo, fixed; in real model, set by controller

# Hip L
F_hip_agon_L = Fmax * activation * C_fatigue
F_hip_ant_L = Fmax * (1 - activation) * C_fatigue
tau_hip_L = moment_arm * (F_hip_agon_L - F_hip_ant_L)
hip_accel_L = tau_hip_L / I_thigh
st.session_state.hip_angle_L += (hip_target_L - st.session_state.hip_angle_L) * 0.2 + hip_accel_L * dt

# Knee L
F_knee_agon_L = Fmax * activation * C_fatigue
F_knee_ant_L = Fmax * (1 - activation) * C_fatigue
tau_knee_L = moment_arm * (F_knee_agon_L - F_knee_ant_L)
knee_accel_L = tau_knee_L / I_shank
st.session_state.knee_angle_L += (knee_target_L - st.session_state.knee_angle_L) * 0.2 + knee_accel_L * dt

# Ankle L (simplified)
st.session_state.ankle_angle_L += (ankle_target_L - st.session_state.ankle_angle_L) * 0.2

# Hip R
F_hip_agon_R = Fmax * activation * C_fatigue
F_hip_ant_R = Fmax * (1 - activation) * C_fatigue
tau_hip_R = moment_arm * (F_hip_agon_R - F_hip_ant_R)
hip_accel_R = tau_hip_R / I_thigh
st.session_state.hip_angle_R += (hip_target_R - st.session_state.hip_angle_R) * 0.2 + hip_accel_R * dt

# Knee R
F_knee_agon_R = Fmax * activation * C_fatigue
F_knee_ant_R = Fmax * (1 - activation) * C_fatigue
tau_knee_R = moment_arm * (F_knee_agon_R - F_knee_ant_R)
knee_accel_R = tau_knee_R / I_shank
st.session_state.knee_angle_R += (knee_target_R - st.session_state.knee_angle_R) * 0.2 + knee_accel_R * dt

# Ankle R (simplified)
st.session_state.ankle_angle_R += (ankle_target_R - st.session_state.ankle_angle_R) * 0.2

# ATP drain
st.session_state.atp -= (abs(F_hip_agon_L) + abs(F_knee_agon_L) + abs(F_hip_agon_R) + abs(F_knee_agon_R)) * 0.0001
if st.session_state.atp < 0: st.session_state.atp = 0

# --- Forward Kinematics ---
hip_x, hip_y = 0.0, 0.08
# Left leg
knee_x_L = hip_x - L_thigh * np.sin(st.session_state.hip_angle_L)
knee_y_L = hip_y - L_thigh * np.cos(st.session_state.hip_angle_L)
ankle_x_L = knee_x_L - L_shank * np.sin(st.session_state.knee_angle_L)
ankle_y_L = knee_y_L - L_shank * np.cos(st.session_state.knee_angle_L)
foot_x_L = ankle_x_L - L_foot * np.sin(st.session_state.ankle_angle_L)
foot_y_L = ankle_y_L - L_foot * np.cos(st.session_state.ankle_angle_L)
# Right leg
knee_x_R = hip_x + L_thigh * np.sin(st.session_state.hip_angle_R)
knee_y_R = hip_y - L_thigh * np.cos(st.session_state.hip_angle_R)
ankle_x_R = knee_x_R + L_shank * np.sin(st.session_state.knee_angle_R)
ankle_y_R = knee_y_R - L_shank * np.cos(st.session_state.knee_angle_R)
foot_x_R = ankle_x_R + L_foot * np.sin(st.session_state.ankle_angle_R)
foot_y_R = ankle_y_R - L_foot * np.cos(st.session_state.ankle_angle_R)

# --- Visualisation ---
fig, ax = plt.subplots(figsize=(4, 3))
# Ground
ax.plot([-0.2, 0.2], [0, 0], 'k-', lw=2)
# Left leg
ax.plot([hip_x, knee_x_L], [hip_y, knee_y_L], 'brown', lw=4, label='L Thigh')
ax.plot([knee_x_L, ankle_x_L], [knee_y_L, ankle_y_L], 'brown', lw=4, label='L Shank')
ax.plot([ankle_x_L, foot_x_L], [ankle_y_L, foot_y_L], 'brown', lw=4, label='L Foot')
# Right leg
ax.plot([hip_x, knee_x_R], [hip_y, knee_y_R], 'blue', lw=4, label='R Thigh')
ax.plot([knee_x_R, ankle_x_R], [knee_y_R, ankle_y_R], 'blue', lw=4, label='R Shank')
ax.plot([ankle_x_R, foot_x_R], [ankle_y_R, foot_y_R], 'blue', lw=4, label='R Foot')
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
# Feet
ax.plot([foot_x_L], [foot_y_L], 'o', color='red', markersize=10, label='L Foot')
ax.plot([foot_x_R], [foot_y_R], 'o', color='blue', markersize=10, label='R Foot')
ax.set_xlim(-0.2, 0.2)
ax.set_ylim(-0.05, head_y + head_radius + 0.05)
ax.axis('off')
ax.legend(loc='upper right', fontsize=8)
st.pyplot(fig)

st.markdown(f"""
ATP: {st.session_state.atp:.1f}  
Hip L angle: {np.rad2deg(st.session_state.hip_angle_L):.1f}°  
Knee L angle: {np.rad2deg(st.session_state.knee_angle_L):.1f}°  
Ankle L angle: {np.rad2deg(st.session_state.ankle_angle_L):.1f}°  
Hip R angle: {np.rad2deg(st.session_state.hip_angle_R):.1f}°  
Knee R angle: {np.rad2deg(st.session_state.knee_angle_R):.1f}°  
Ankle R angle: {np.rad2deg(st.session_state.ankle_angle_R):.1f}°  
Gait phase: {st.session_state.gait_phase:.2f}  
""")
