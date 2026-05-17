import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout="wide")
st.title("A7DOv13 — Concise Anatomical Walker")

# --- Parameters ---
L_thigh, L_shank, L_foot, L_torso = 0.12, 0.12, 0.08, 0.18
head_radius, L_upperarm, L_forearm, shoulder_width = 0.03, 0.10, 0.10, 0.10
Fmax, moment_arm, ATP_max = 100, 0.04, 100.0

# --- State ---
for key, val in {
    "gait_phase": 0, "step_count": 0, "crawl_phase": 0,
    "atp": ATP_max, "mode": "stand"
}.items():
    if key not in st.session_state: st.session_state[key] = val

# --- UI ---
cols = st.columns(6)
do_step = cols[0].button("STEP")
stand = cols[1].button("STAND")
sit = cols[2].button("SIT")
crawl = cols[3].button("CRAWL")
crawl_step = cols[4].button("CRAWL STEP")
reset = cols[5].button("RESET")

if reset:
    for k in ["gait_phase", "step_count", "crawl_phase", "atp", "mode"]:
        st.session_state[k] = {"gait_phase": 0, "step_count": 0, "crawl_phase": 0, "atp": ATP_max, "mode": "stand"}[k]
if stand: st.session_state.mode = "stand"
if sit: st.session_state.mode = "sit"
if crawl: st.session_state.mode = "crawl"
if do_step:
    st.session_state.mode = "walk"
    st.session_state.gait_phase += 1
    st.session_state.step_count += 1
if crawl_step:
    st.session_state.mode = "crawl"
    st.session_state.crawl_phase += 1
    st.session_state.step_count += 1

phase = st.session_state.gait_phase % 2
crawl_phase = st.session_state.crawl_phase % 4
C_fatigue = st.session_state.atp / ATP_max

# --- Joint Angles ---
if st.session_state.mode == "stand":
    hip_L = hip_R = np.deg2rad(15); knee_L = knee_R = np.deg2rad(20)
    ankle_L = ankle_R = np.deg2rad(0); shoulder_L = np.deg2rad(-10); shoulder_R = np.deg2rad(10)
    elbow_L = elbow_R = np.deg2rad(20)
elif st.session_state.mode == "sit":
    hip_L = hip_R = knee_L = knee_R = np.deg2rad(90)
    ankle_L = ankle_R = np.deg2rad(0); shoulder_L = np.deg2rad(-10); shoulder_R = np.deg2rad(10)
    elbow_L = elbow_R = np.deg2rad(20)
elif st.session_state.mode == "crawl":
    # Contralateral crawl step pattern
    if crawl_phase == 0:
        hip_L, knee_L, ankle_L = np.deg2rad(110), np.deg2rad(110), 0
        hip_R, knee_R, ankle_R = np.deg2rad(90), np.deg2rad(90), 0
        shoulder_L, shoulder_R = np.deg2rad(110), np.deg2rad(70)
        elbow_L, elbow_R = np.deg2rad(110), np.deg2rad(70)
    elif crawl_phase == 1 or crawl_phase == 3:
        hip_L = hip_R = knee_L = knee_R = np.deg2rad(90)
        ankle_L = ankle_R = 0; shoulder_L = shoulder_R = np.deg2rad(70)
        elbow_L = elbow_R = np.deg2rad(70)
    else:
        hip_L, knee_L, ankle_L = np.deg2rad(90), np.deg2rad(90), 0
        hip_R, knee_R, ankle_R = np.deg2rad(110), np.deg2rad(110), 0
        shoulder_L, shoulder_R = np.deg2rad(70), np.deg2rad(110)
        elbow_L, elbow_R = np.deg2rad(70), np.deg2rad(110)
else:
    hip_L = np.deg2rad(10) if phase == 0 else np.deg2rad(30)
    knee_L = np.deg2rad(20) if phase == 0 else np.deg2rad(60)
    ankle_L = np.deg2rad(-5) if phase == 0 else np.deg2rad(10)
    hip_R = np.deg2rad(30) if phase == 0 else np.deg2rad(10)
    knee_R = np.deg2rad(60) if phase == 0 else np.deg2rad(20)
    ankle_R = np.deg2rad(10) if phase == 0 else np.deg2rad(-5)
    shoulder_L = np.deg2rad(-30) if phase == 0 else np.deg2rad(30)
    shoulder_R = np.deg2rad(30) if phase == 0 else np.deg2rad(-30)
    elbow_L = elbow_R = np.deg2rad(20)

# --- Muscle Forces & Torques ---
def muscle_torque(activation):
    F_agon = Fmax * activation * C_fatigue
    F_ant = Fmax * (1 - activation) * C_fatigue
    tau = moment_arm * (F_agon - F_ant)
    return tau, F_agon, F_ant, activation

def act(mode, swing, stance, crawl, sit, phase, is_L):
    if mode == "crawl": return crawl
    if mode == "sit": return sit
    if mode == "stand": return stance
    return swing if (phase == 0 if is_L else phase == 1) else stance

tau_hip_L, _, _, act_hip_L = muscle_torque(act(st.session_state.mode, activation_leg_swing, activation_leg_stance, activation_crawl, activation_sit, phase, True))
tau_hip_R, _, _, act_hip_R = muscle_torque(act(st.session_state.mode, activation_leg_swing, activation_leg_stance, activation_crawl, activation_sit, phase, False))
tau_knee_L, _, _, act_knee_L = muscle_torque(act(st.session_state.mode, activation_leg_swing, activation_leg_stance, activation_crawl, activation_sit, phase, True))
tau_knee_R, _, _, act_knee_R = muscle_torque(act(st.session_state.mode, activation_leg_swing, activation_leg_stance, activation_crawl, activation_sit, phase, False))
tau_ankle_L, _, _, act_ankle_L = muscle_torque(act(st.session_state.mode, activation_leg_swing, activation_leg_stance, activation_crawl, activation_sit, phase, True))
tau_ankle_R, _, _, act_ankle_R = muscle_torque(act(st.session_state.mode, activation_leg_swing, activation_leg_stance, activation_crawl, activation_sit, phase, False))
tau_shoulder_L, _, _, act_shoulder_L = muscle_torque(act(st.session_state.mode, activation_arm_swing, activation_arm_stance, activation_crawl, activation_sit, phase, True))
tau_shoulder_R, _, _, act_shoulder_R = muscle_torque(act(st.session_state.mode, activation_arm_swing, activation_arm_stance, activation_crawl, activation_sit, phase, False))
tau_elbow_L, _, _, act_elbow_L = muscle_torque(0.85 if st.session_state.mode == "crawl" else 0.5)
tau_elbow_R, _, _, act_elbow_R = muscle_torque(0.85 if st.session_state.mode == "crawl" else 0.5)

# --- ATP drain per joint ---
atp_drain = sum([
    abs(tau_hip_L), abs(tau_hip_R), abs(tau_knee_L), abs(tau_knee_R),
    abs(tau_ankle_L), abs(tau_ankle_R), abs(tau_shoulder_L), abs(tau_shoulder_R),
    abs(tau_elbow_L), abs(tau_elbow_R)
]) * 0.001
st.session_state.atp = max(0, st.session_state.atp - atp_drain)

# --- Forward Kinematics ---
hip_x, hip_y = 0.0, 0.08
shoulder_y = hip_y + L_torso
shoulder_left_x = hip_x - shoulder_width / 2
shoulder_right_x = hip_x + shoulder_width / 2
knee_x_L = hip_x - L_thigh * np.sin(hip_L)
knee_y_L = hip_y - L_thigh * np.cos(hip_L)
ankle_x_L = knee_x_L - L_shank * np.sin(knee_L)
ankle_y_L = knee_y_L - L_shank * np.cos(knee_L)
foot_x_L = ankle_x_L - L_foot * np.sin(ankle_L)
foot_y_L = ankle_y_L - L_foot * np.cos(ankle_L)
knee_x_R = hip_x + L_thigh * np.sin(hip_R)
knee_y_R = hip_y - L_thigh * np.cos(hip_R)
ankle_x_R = knee_x_R + L_shank * np.sin(knee_R)
ankle_y_R = knee_y_R - L_shank * np.cos(knee_R)
foot_x_R = ankle_x_R + L_foot * np.sin(ankle_R)
foot_y_R = ankle_y_R - L_foot * np.cos(ankle_R)
elbow_x_L = shoulder_left_x + L_upperarm * np.sin(shoulder_L)
elbow_y_L = shoulder_y - L_upperarm * np.cos(shoulder_L)
wrist_x_L = elbow_x_L + L_forearm * np.sin(shoulder_L + elbow_L)
wrist_y_L = elbow_y_L - L_forearm * np.cos(shoulder_L + elbow_L)
elbow_x_R = shoulder_right_x + L_upperarm * np.sin(shoulder_R)
elbow_y_R = shoulder_y - L_upperarm * np.cos(shoulder_R)
wrist_x_R = elbow_x_R + L_forearm * np.sin(shoulder_R + elbow_R)
wrist_y_R = elbow_y_R - L_forearm * np.cos(shoulder_R + elbow_R)

def limb_colour(activation):
    # Map activation [0,1] to red (high) or blue (low)
    return (activation, 0, 1 - activation)

fig, ax = plt.subplots(figsize=(4, 3))
ax.plot([-0.2, 0.2], [0, 0], 'k-', lw=2)
ax.plot([hip_x, knee_x_L], [hip_y, knee_y_L], color=limb_colour(act_hip_L), lw=4)
ax.plot([knee_x_L, ankle_x_L], [knee_y_L, ankle_y_L], color=limb_colour(act_knee_L), lw=4)
ax.plot([ankle_x_L, foot_x_L], [ankle_y_L, foot_y_L], color=limb_colour(act_ankle_L), lw=4)
ax.plot([hip_x, knee_x_R], [hip_y, knee_y_R], color=limb_colour(act_hip_R), lw=4)
ax.plot([knee_x_R, ankle_x_R], [knee_y_R, ankle_y_R], color=limb_colour(act_knee_R), lw=4)
ax.plot([ankle_x_R, foot_x_R], [ankle_y_R, foot_y_R], color=limb_colour(act_ankle_R), lw=4)
ax.plot([hip_x, hip_x], [hip_y, shoulder_y], 'g-', lw=6)
ax.plot([shoulder_left_x, shoulder_right_x], [shoulder_y, shoulder_y], 'g-', lw=6)
head_y = shoulder_y + head_radius + 0.01
ax.add_patch(plt.Circle((hip_x, head_y), head_radius, color='orange', zorder=10))
ax.plot([shoulder_left_x, elbow_x_L], [shoulder_y, elbow_y_L], color=limb_colour(act_shoulder_L), lw=4)
ax.plot([elbow_x_L, wrist_x_L], [elbow_y_L, wrist_y_L], color=limb_colour(act_elbow_L), lw=4)
ax.plot([shoulder_right_x, elbow_x_R], [shoulder_y, elbow_y_R], color=limb_colour(act_shoulder_R), lw=4)
ax.plot([elbow_x_R, wrist_x_R], [elbow_y_R, wrist_y_R], color=limb_colour(act_elbow_R), lw=4)
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
Hip L act: {act_hip_L:.2f} | Hip R act: {act_hip_R:.2f}  
Knee L act: {act_knee_L:.2f} | Knee R act: {act_knee_R:.2f}  
Ankle L act: {act_ankle_L:.2f} | Ankle R act: {act_ankle_R:.2f}  
Shoulder L act: {act_shoulder_L:.2f} | Shoulder R act: {act_shoulder_R:.2f}  
Elbow L act: {act_elbow_L:.2f} | Elbow R act: {act_elbow_R:.2f}  
""")
