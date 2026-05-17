import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

from body import default_body
from muscles import default_muscles, muscle_force
from joints import default_joints, joint_torque
from development import stages, stage_from_growth
from dna import init_dna, grow, developmental_mode

st.set_page_config(layout="wide")
st.title("A7DOv13 — Modular Anatomical Walker")

# --- DNA initialisation ---
if "DNA" not in st.session_state:
    st.session_state.DNA = init_dna()

# --- Grow button ---
if st.button("GROW"):
    st.session_state.DNA = grow(st.session_state.DNA)

# --- Mode selection from DNA ---
mode = developmental_mode(st.session_state.DNA)
st.session_state.mode = mode

# --- Use DNA values for segment lengths and strengths ---
limb_lengths = st.session_state.DNA["limb_lengths"]
muscle_strength = st.session_state.DNA["muscle_strength"]
ATP_max = st.session_state.DNA["ATP_max"]

# --- Body, Muscles, Joints initialisation ---
body = default_body()
muscles = default_muscles()
joints = default_joints()

# --- Override body/muscles with DNA values ---
for seg in limb_lengths:
    body["limb_lengths"][seg] = limb_lengths[seg]
for joint in muscle_strength:
    muscles["muscle_strength"][joint] = muscle_strength[joint]
muscles["ATP_max"] = ATP_max

# --- Set joint angles based on mode ---
if mode == "emwomb":
    joints["angles"]["hip"] = joints["angles"]["knee"] = 0
elif mode == "sit":
    joints["angles"]["hip"] = joints["angles"]["knee"] = np.deg2rad(90)
elif mode == "crawl":
    joints["angles"]["hip"] = joints["angles"]["knee"] = np.deg2rad(110)
elif mode == "stand":
    joints["angles"]["hip"] = joints["angles"]["knee"] = np.deg2rad(15)
elif mode == "walk":
    joints["angles"]["hip"] = np.deg2rad(30)
    joints["angles"]["knee"] = np.deg2rad(60)
else:
    joints["angles"]["hip"] = joints["angles"]["knee"] = np.deg2rad(10)

# --- Calculate muscle forces and torques ---
F_hip = muscle_force(muscles["muscle_strength"]["hip"], muscles["activation"]["hip"], muscles["fatigue"])
F_knee = muscle_force(muscles["muscle_strength"]["knee"], muscles["activation"]["knee"], muscles["fatigue"])
tau_hip = joint_torque(0.04, F_hip, F_hip * 0.5)  # Example: antagonist is half agonist
tau_knee = joint_torque(0.04, F_knee, F_knee * 0.5)

# --- Forward kinematics (left leg only for demo) ---
hip_x, hip_y = 0.0, 0.08
thigh_L = body["limb_lengths"]["thigh"]
shank_L = body["limb_lengths"]["shank"]
foot_L = body["limb_lengths"]["foot"]
torso_L = body["limb_lengths"]["torso"]
head_radius = 0.03

hip_angle = joints["angles"]["hip"]
knee_angle = joints["angles"]["knee"]

knee_x = hip_x - thigh_L * np.sin(hip_angle)
knee_y = hip_y - thigh_L * np.cos(hip_angle)
ankle_x = knee_x - shank_L * np.sin(knee_angle)
ankle_y = knee_y - shank_L * np.cos(knee_angle)
foot_x = ankle_x - foot_L * np.sin(0)
foot_y = ankle_y - foot_L * np.cos(0)
shoulder_y = hip_y + torso_L
head_y = shoulder_y + head_radius + 0.01

fig, ax = plt.subplots(figsize=(4, 3))
ax.plot([hip_x, knee_x], [hip_y, knee_y], 'brown', lw=4)
ax.plot([knee_x, ankle_x], [knee_y, ankle_y], 'brown', lw=4)
ax.plot([ankle_x, foot_x], [ankle_y, foot_y], 'brown', lw=4)
ax.plot([hip_x, hip_x], [hip_y, shoulder_y], 'g-', lw=6)
ax.add_patch(plt.Circle((hip_x, head_y), head_radius, color='orange', zorder=10))
ax.set_xlim(-0.2, 0.2)
ax.set_ylim(-0.05, head_y + head_radius + 0.05)
ax.axis('off')
st.pyplot(fig)

st.markdown(f"""
Mode: {mode}  
DNA limb lengths: {limb_lengths}  
DNA muscle strengths: {muscle_strength}  
ATP max: {ATP_max}  
Hip torque: {tau_hip:.2f}  
Knee torque: {tau_knee:.2f}
""")
