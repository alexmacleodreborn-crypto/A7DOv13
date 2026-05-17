import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout="wide")
st.title("A7DOv13 — Anatomical Walking (Linked to Equations)")

# State variables for anatomical joints
if "hip_angle" not in st.session_state:
    st.session_state.hip_angle = np.deg2rad(10)  # radians
if "knee_angle" not in st.session_state:
    st.session_state.knee_angle = np.deg2rad(20)
if "ankle_angle" not in st.session_state:
    st.session_state.ankle_angle = np.deg2rad(-5)
if "atp" not in st.session_state:
    st.session_state.atp = 100.0

# Parameters
thigh_length = 0.12
shank_length = 0.12
foot_length = 0.08
torso_height = 0.18
head_radius = 0.03

# Muscle force and torque equations (example)
Fmax = 100
activation = 0.8
C_fatigue = st.session_state.atp / 100.0
moment_arm = 0.04

# Calculate muscle forces
F_agonist = Fmax * activation * C_fatigue
F_antagonist = Fmax * (1 - activation) * C_fatigue
tau_knee = moment_arm * (F_agonist - F_antagonist)

# Joint dynamics (simplified)
I_knee = 0.01
knee_accel = tau_knee / I_knee
st.session_state.knee_angle += knee_accel * 0.01  # dt

# ATP drain
st.session_state.atp -= abs(F_agonist) * 0.0001

# Forward kinematics for stick figure
hip_x, hip_y = 0.0, 0.08
knee_x = hip_x + thigh_length * np.sin(st.session_state.hip_angle)
knee_y = hip_y - thigh_length * np.cos(st.session_state.hip_angle)
ankle_x = knee_x + shank_length * np.sin(st.session_state.knee_angle)
ankle_y = knee_y - shank_length * np.cos(st.session_state.knee_angle)
foot_x = ankle_x + foot_length * np.sin(st.session_state.ankle_angle)
foot_y = ankle_y - foot_length * np.cos(st.session_state.ankle_angle)

# Visualisation
fig, ax = plt.subplots(figsize=(4, 3))
ax.plot([hip_x, knee_x], [hip_y, knee_y], 'brown', lw=4, label='Thigh')
ax.plot([knee_x, ankle_x], [knee_y, ankle_y], 'brown', lw=4, label='Shank')
ax.plot([ankle_x, foot_x], [ankle_y, foot_y], 'brown', lw=4, label='Foot')
ax.plot([hip_x, hip_x], [hip_y, hip_y + torso_height], 'g-', lw=6, label='Torso')
head_y = hip_y + torso_height + head_radius + 0.01
head = plt.Circle((hip_x, head_y), head_radius, color='orange', zorder=10)
ax.add_patch(head)
ax.set_xlim(-0.2, 0.2)
ax.set_ylim(-0.05, head_y + head_radius + 0.05)
ax.axis('off')
ax.legend(loc='upper right', fontsize=8)
st.pyplot(fig)

st.markdown(f"""
ATP: {st.session_state.atp:.1f}  
Knee torque: {tau_knee:.2f}  
Knee angle: {np.rad2deg(st.session_state.knee_angle):.1f}°
""")
