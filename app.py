import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from dna import init_dna, grow, developmental_mode

st.set_page_config(layout="wide")
st.title("A7DOv13 — Modular Developmental Organism")

if "DNA" not in st.session_state:
    st.session_state.DNA = init_dna()

if st.button("GROW"):
    st.session_state.DNA = grow(st.session_state.DNA)

mode = developmental_mode(st.session_state.DNA)
st.session_state.mode = mode

limb_lengths = st.session_state.DNA["limb_lengths"]
muscle_strength = st.session_state.DNA["muscle_strength"]
ATP_max = st.session_state.DNA["ATP_max"]
organs = st.session_state.DNA["organ_development"]

# Set joint angles based on mode
if mode == "emwomb":
    hip_angle = knee_angle = 0
elif mode == "sit":
    hip_angle = knee_angle = np.deg2rad(90)
elif mode == "crawl":
    hip_angle = knee_angle = np.deg2rad(110)
elif mode == "stand":
    hip_angle = knee_angle = np.deg2rad(15)
elif mode == "walk":
    hip_angle = np.deg2rad(30)
    knee_angle = np.deg2rad(60)
else:
    hip_angle = knee_angle = np.deg2rad(10)

hip_x, hip_y = 0.0, 0.08
thigh_L = limb_lengths["thigh"]
shank_L = limb_lengths["shank"]
foot_L = limb_lengths["foot"]
torso_L = limb_lengths["torso"]
head_radius = 0.03

knee_x = hip_x - thigh_L * np.sin(hip_angle)
knee_y = hip_y - thigh_L * np.cos(hip_angle)
ankle_x = knee_x - shank_L * np.sin(knee_angle)
ankle_y = knee_y - shank_L * np.cos(knee_angle)
foot_x = ankle_x - foot_L * np.sin(0)
foot_y = ankle_y - foot_L * np.cos(0)
shoulder_y = hip_y + torso_L
head_y = shoulder_y + head_radius + 0.01

fig, ax = plt.subplots(figsize=(4, 3))
heart_maturity = organs["heart"]
lungs_maturity = organs["lungs"]
spine_maturity = organs["spine"]
cord_attached = organs["umbilical_cord"] > 0.5
ax.add_patch(plt.Circle((0, 0.15), 0.015 + 0.005 * (1 if st.session_state.DNA["heartbeat"] else 0), color=(1, 0, 0, heart_maturity)))
ax.add_patch(plt.Circle((-0.025, 0.13), 0.018 * lungs_maturity, color=(0, 0.5, 1, lungs_maturity)))
ax.add_patch(plt.Circle((0.025, 0.13), 0.018 * lungs_maturity, color=(0, 0.5, 1, lungs_maturity)))
ax.plot([0, 0], [0.08, 0.13], color='brown', lw=2 + 4 * spine_maturity)
if cord_attached:
    ax.plot([0, -0.1], [0.08, 0.0], color='orange', lw=2)
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
Heartbeat: {"Yes" if st.session_state.DNA["heartbeat"] else "No"}  
Breathing: {"Yes" if st.session_state.DNA["breathing"] else "No"}  
Cord attached: {"Yes" if cord_attached else "No"}  
Heart maturity: {heart_maturity:.2f}  
Lungs maturity: {lungs_maturity:.2f}  
Spine maturity: {spine_maturity:.2f}  
DNA limb lengths: {limb_lengths}  
DNA muscle strengths: {muscle_strength}  
ATP max: {ATP_max}
""")
