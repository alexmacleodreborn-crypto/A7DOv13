import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout="wide")
st.title("A7DOv13 — Anatomical Walker (Stand/Step/Sit/Crawl, Muscles & Joints)")

# --- Parameters ---
L_thigh = 0.12
L_shank = 0.12
L_foot = 0.08
L_torso = 0.18
head_radius = 0.03
L_upperarm = 0.10
L_forearm = 0.10
shoulder_width = 0.10
Fmax = 100
moment_arm = 0.04
ATP_max = 100.0

# --- State ---
if "gait_phase" not in st.session_state:
    st.session_state.gait_phase = 0
if "step_count" not in st.session_state:
    st.session_state.step_count = 0
if "crawl_phase" not in st.session_state:
    st.session_state.crawl_phase = 0
if "atp" not in st.session_state:
    st.session_state.atp = ATP_max
if "mode" not in st.session_state:
    st.session_state.mode = "stand"  # "stand", "walk", "sit", "crawl"

# --- UI Buttons ---
colA, colB, colC, colD, colE, colF = st.columns(6)
with colA:
    do_step = st.button("STEP")
with colB:
    stand = st.button("STAND")
with colC:
    sit = st.button("SIT")
with colD:
    crawl = st.button("CRAWL")
with colE:
    crawl_step = st.button("CRAWL STEP")
with colF:
    reset = st.button("RESET")

if reset:
    st.session_state.gait_phase = 0
    st.session_state.step_count = 0
    st.session_state.crawl_phase = 0
    st.session_state.atp = ATP_max
    st.session_state.mode = "stand"

if stand:
    st.session_state.mode = "stand"

if sit:
    st.session_state.mode = "sit"

if crawl:
    st.session_state.mode = "crawl"

if do_step:
    st.session_state.mode = "walk"
    st.session_state.gait_phase += 1
    st.session_state.step_count += 1

if crawl_step:
    st.session_state.mode = "crawl"
    st.session_state.crawl_phase += 1
    st.session_state.step_count += 1

# --- Gait Logic: Step-based, alternating legs ---
phase = st.session_state.gait_phase % 2
crawl_phase = st.session_state.crawl_phase % 4

# --- Muscle Activation ---
activation_leg_swing = 0.9
activation_leg_stance = 0.3
activation_arm_swing = 0.8
activation_arm_stance = 0.2
activation_sit = 0.4
activation_crawl = 0.6
activation_crawl_elbow = 0.85 if st.session_state.mode == "crawl" else 0.5
C_fatigue = st.session_state.atp / ATP_max

# --- Joint Angles ---
if st.session_state.mode == "stand":
    hip_angle_L = hip_angle_R = np.deg2rad(15)
    knee_angle_L = knee_angle_R = np.deg2rad(20)
    ankle_angle_L = ankle_angle_R = np.deg2rad(0)
    shoulder_angle_L = np.deg2rad(-10)
    shoulder_angle_R = np.deg2rad(10)
elif st.session_state.mode == "sit":
    hip_angle_L = hip_angle_R = np.deg2rad(90)
    knee_angle_L = knee_angle_R = np.deg2rad(90)
    ankle_angle_L = ankle_angle_R = np.deg2rad(0)
    shoulder_angle_L = np.deg2rad(-10)
    shoulder_angle_R = np.deg2rad(10)
elif st.session_state.mode == "crawl":
    # Contralateral crawl step pattern
    # 0: Left arm/right leg swing; 1: Pause; 2: Right arm/left leg swing; 3: Pause
    if crawl_phase == 0:
        hip_angle_L = np.deg2rad(110)
        knee_angle_L = np.deg2rad(110)
        ankle_angle_L = np.deg2rad(0)
        hip_angle_R = np.deg2rad(90)
        knee_angle_R = np.deg2rad(90)
        ankle_angle_R = np.deg2rad(0)
        shoulder_angle_L = np.deg2rad(110)
        shoulder_angle_R = np.deg2rad(70)
        elbow_angle_L = np.deg2rad(110)
        elbow_angle_R = np.deg2rad(70)
    elif crawl_phase == 1:
        hip_angle_L = np.deg2rad(90)
        knee_angle_L = np.deg2rad(90)
        ankle_angle_L = np.deg2rad(0)
        hip_angle_R = np.deg2rad(90)
        knee_angle_R = np.deg2rad(90)
        ankle_angle_R = np.deg2rad(0)
        shoulder_angle_L = np.deg2rad(70)
        shoulder_angle_R = np.deg2rad(70)
        elbow_angle_L = np.deg2rad(70)
        elbow_angle_R = np.deg2rad(70)
    elif crawl_phase == 2:
        hip_angle_L = np.deg2rad(90)
        knee_angle_L = np.deg2rad(90)
        ankle_angle_L = np.deg2rad(0)
        hip_angle_R = np.deg2rad(110)
        knee_angle_R = np.deg2rad(110)
        ankle_angle_R = np.deg2rad(0)
        shoulder_angle_L = np.deg2rad(70)
        shoulder_angle_R = np.deg2rad(110)
        elbow_angle_L = np.deg2rad(70)
        elbow_angle_R = np.deg2rad(110)
    else:
        hip_angle_L = np.deg2rad(90)
        knee_angle_L = np.deg2rad(90)
        ankle_angle_L = np.deg2rad(0)
        hip_angle_R = np.deg2rad(90)
        knee_angle_R = np.deg2rad(90)
        ankle_angle_R = np.deg2rad(0)
        shoulder_angle_L = np.deg2rad(70)
        shoulder_angle_R = np.deg2rad(70)
        elbow_angle_L = np.deg2rad(70)
        elbow_angle_R = np.deg2rad(70)
else:
    hip_angle_L = np.deg2rad(10) if phase == 0 else np.deg2rad(30)
    knee_angle_L = np.deg2rad(20) if phase == 0 else np.deg2rad(60)
    ankle_angle_L = np.deg2rad(-5) if phase == 0 else np.deg2rad(10)
    hip_angle_R = np.deg2rad(30) if phase == 0 else np.deg2rad(10)
    knee_angle_R = np.deg2rad(60) if phase == 0 else np.deg2rad(20)
    ankle_angle_R = np.deg2rad(10) if phase == 0 else np.deg2rad(-5)
    shoulder_angle_L = np.deg2rad(-30) if phase == 0 else np.deg2rad(30)
    shoulder_angle_R = np.deg2rad(30) if phase == 0 else np.deg2rad(-30)
    elbow_angle_L = elbow_angle_R = np.deg2rad(20)

# --- Muscle Forces & Torques ---
def muscle_torque(activation, C_fatigue):
    F_agon = Fmax * activation * C_fatigue
    F_ant = Fmax * (1 - activation) * C_fatigue
    tau = moment_arm * (F_agon - F_ant)
    return tau, F_agon, F_ant

# Hips
tau_hip_L, F_hip_agon_L, F_hip_ant_L = muscle_torque(
    activation_crawl if st.session_state.mode == "crawl" else activation_sit if st.session_state.mode == "sit" else (activation_leg_stance if phase == 0 or st.session_state.mode == "stand" else activation_leg_swing), C_fatigue)
tau_hip_R, F_hip_agon_R, F_hip_ant_R = muscle_torque(
    activation_crawl if st.session_state.mode == "crawl" else activation_sit if st.session_state.mode == "sit" else (activation_leg_swing if phase == 0 and st.session_state.mode == "walk" else activation_leg_stance), C_fatigue)
# Knees
tau_knee_L, F_knee_agon_L, F_knee_ant_L = muscle_torque(
    activation_crawl if st.session_state.mode == "crawl" else activation_sit if st.session_state.mode == "sit" else (activation_leg_stance if phase == 0 or st.session_state.mode == "stand" else activation_leg_swing), C_fatigue)
tau_knee_R, F_knee_agon_R, F_knee_ant_R = muscle_torque(
    activation_crawl if st.session_state.mode == "crawl" else activation_sit if st.session_state.mode == "sit" else (activation_leg_swing if phase == 0 and st.session_state.mode == "walk" else activation_leg_stance), C_fatigue)
# Ankles
tau_ankle_L, F_ankle_agon_L, F_ankle_ant_L = muscle_torque(
    activation_crawl if st.session_state.mode == "crawl" else activation_sit if st.session_state.mode == "sit" else (activation_leg_stance if phase == 0 or st.session_state.mode == "stand" else activation_leg_swing), C_fatigue)
tau_ankle_R, F_ankle_agon_R, F_ankle_ant_R = muscle_torque(
    activation_crawl if st.session_state.mode == "crawl" else activation_sit if st.session_state.mode == "sit" else (activation_leg_swing if phase == 0 and st.session_state.mode == "walk" else activation_leg_stance), C_fatigue)
# Shoulders
tau_shoulder_L, F_shoulder_agon_L, F_shoulder_ant_L = muscle_torque(
    activation_crawl if st.session_state.mode == "crawl" else activation_arm_stance if st.session_state.mode == "sit" else (activation_arm_swing if phase == 1 and st.session_state.mode == "walk" else activation_arm_stance), C_fatigue)
tau_shoulder_R, F_shoulder_agon_R, F_shoulder_ant_R = muscle_torque(
    activation_crawl if st.session_state.mode == "crawl" else activation_arm_stance if st.session_state.mode == "sit" else (activation_arm_swing if phase == 0 and st.session_state.mode == "walk" else activation_arm_stance), C_fatigue)
# Elbows (crawl-specific activation)
tau_elbow_L, F_elbow_agon_L, F_elbow_ant_L = muscle_torque(activation_crawl_elbow, C_fatigue)
tau_elbow_R, F_elbow_agon_R, F_elbow_ant_R = muscle_torque(activation_crawl_elbow, C_fatigue)

# --- ATP drain per joint ---
atp_drain = (
    abs(F_hip_agon_L) + abs(F_hip_agon_R) +
    abs(F_knee_agon_L) + abs(F_knee_agon_R) +
    abs(F_ankle_agon_L) + abs(F_ankle_agon_R) +
    abs(F_shoulder_agon_L) + abs(F_shoulder_agon_R) +
    abs(F_elbow_agon_L) + abs(F_elbow_agon_R)
) * 0.0001
st.session_state.atp -= atp_drain
if st.session_state.atp < 0: st.session_state.atp = 0

# --- Forward Kinematics ---
hip_x, hip_y = 0.0, 0.08
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
ax.plot([-0.2, 0.2], [0, 0], 'k-', lw=2)
ax.plot([hip_x, knee_x_L], [hip_y, knee_y_L], 'brown', lw=4)
ax.plot([knee_x_L, ankle_x_L], [knee_y_L, ankle_y_L], 'brown', lw=4)
ax.plot([ankle_x_L, foot_x_L], [ankle_y_L, foot_y_L], 'brown', lw=4)
ax.plot([hip_x, knee_x_R], [hip_y, knee_y_R], 'blue', lw=4)
ax.plot([knee_x_R, ankle_x_R], [knee_y_R, ankle_y_R], 'blue', lw=4)
ax.plot([ankle_x_R, foot_x_R], [ankle_y_R, foot_y_R], 'blue', lw=4)
ax.plot([hip_x, hip_x], [hip_y, shoulder_y], 'g-', lw=6)
ax.plot([shoulder_left_x, shoulder_right_x], [shoulder_y, shoulder_y], 'g-', lw=6)
head_y = shoulder_y + head_radius + 0.01
head = plt.Circle((hip_x, head_y), head_radius, color='orange', zorder=10)
ax.add_patch(head)
ax.plot([shoulder_left_x, elbow_x_L], [shoulder_y, elbow_y_L], 'purple', lw=4)
ax.plot([elbow_x_L, wrist_x_L], [elbow_y_L, wrist_y_L], 'purple', lw=4)
ax.plot([shoulder_right_x, elbow_x_R], [shoulder_y, elbow_y_R], 'purple', lw=4)
ax.plot([elbow_x_R, wrist_x_R], [elbow_y_R, wrist_y_R], 'purple', lw=4)
ax.plot([foot_x_L], [foot_y_L], 'o', color='red', markersize=10)
ax.plot([foot_x_R], [foot_y_R], 'o', color='blue', markersize=10)
ax.set_xlim(-0.2, 0.2)
ax.set_ylim(-0.05, head_y + head_radius + 0.05)
ax.axis('off')
st.pyplot(fig)

st.markdown(f"""
Step count: {st.session_state.step_count}  
Mode: {st.session_state.mode}  
ATP: {st.session_state.atp:.1f}  
Hip L torque: {tau_hip_L:.2f}  
Hip R torque: {tau_hip_R:.2f}  
Knee L torque: {tau_knee_L:.2f}  
Knee R torque: {tau_knee_R:.2f}  
Ankle L torque: {tau_ankle_L:.2f}  
Ankle R torque: {tau_ankle_R:.2f}  
Shoulder L torque: {tau_shoulder_L:.2f}  
Shoulder R torque: {tau_shoulder_R:.2f}  
Elbow L torque: {tau_elbow_L:.2f}  
Elbow R torque: {tau_elbow_R:.2f}  
""")

if st.session_state.mode == "crawl":
    st.markdown(f"""
    Elbow L torque (crawl): {tau_elbow_L:.2f}  
    Elbow R torque (crawl): {tau_elbow_R:.2f}  
    Elbow activation (crawl): {activation_crawl_elbow:.2f}
    """)
