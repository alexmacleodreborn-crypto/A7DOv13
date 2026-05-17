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

# --- Joint Angles & Muscle Activation ---
def get_angles_and_activation(mode, phase, crawl_phase):
    # Default activations
    act_leg_swing, act_leg_stance = 0.9, 0.3
    act_arm_swing, act_arm_stance = 0.8, 0.2
    act_sit, act_crawl, act_crawl_elbow = 0.4, 0.6, 0.85

    if mode == "stand":
        angles = [15, 15, 20, 20, 0, 0, -10, 10, 20, 20]
        acts = [act_leg_stance]*6 + [act_arm_stance]*2 + [0.5, 0.5]
    elif mode == "sit":
        angles = [90, 90, 90, 90, 0, 0, -10, 10, 20, 20]
        acts = [act_sit]*6 + [act_arm_stance]*2 + [0.5, 0.5]
    elif mode == "crawl":
        # Contralateral crawl step pattern
        if crawl_phase == 0:
            angles = [110, 90, 110, 90, 0, 0, 110, 70, 110, 70]
        elif crawl_phase == 1 or crawl_phase == 3:
            angles = [90, 90, 90, 90, 0, 0, 70, 70, 70, 70]
        else:
            angles = [90, 110, 90, 110, 0, 0, 70, 110, 70, 110]
        acts = [act_crawl]*6 + [act_crawl]*2 + [act_crawl_elbow, act_crawl_elbow]
    else:  # walk
        if phase == 0:
            angles = [10, 30, 20, 60, -5, 10, -30, 30, 20, 20]
            acts = [act_leg_swing, act_leg_stance, act_leg_swing, act_leg_stance,
                    act_leg_swing, act_leg_stance, act_arm_swing, act_arm_stance, 0.5, 0.5]
        else:
            angles = [30, 10, 60, 20, 10, -5, 30, -30, 20, 20]
            acts = [act_leg_stance, act_leg_swing, act_leg_stance, act_leg_swing,
                    act_leg_stance, act_leg_swing, act_arm_stance, act_arm_swing, 0.5, 0.5]
    # Angles: hip_L, hip_R, knee_L, knee_R, ankle_L, ankle_R, shoulder_L, shoulder_R, elbow_L, elbow_R
    return [np.deg2rad(a) for a in angles], acts

angles, acts = get_angles_and_activation(st.session_state.mode, phase, crawl_phase)
(hip_L, hip_R, knee_L, knee_R, ankle_L, ankle_R, shoulder_L, shoulder_R, elbow_L, elbow_R) = angles
(act_hip_L, act_hip_R, act_knee_L, act_knee_R, act_ankle_L, act_ankle_R, act_shoulder_L, act_shoulder_R, act_elbow_L, act_elbow_R) = acts

def muscle_torque(activation):
    F_agon = Fmax * activation * C_fatigue
    F_ant = Fmax * (1 - activation) * C_fatigue
    tau = moment_arm * (F_agon - F_ant)
    return tau, activation

tau_hip_L, _ = muscle_torque(act_hip_L)
tau_hip_R, _ = muscle_torque(act_hip_R)
tau_knee_L, _ = muscle_torque(act_knee_L)
tau_knee_R, _ = muscle_torque(act_knee_R)
tau_ankle_L, _ = muscle_torque(act_ankle_L)
tau_ankle_R, _ = muscle_torque(act_ankle_R)
tau_shoulder_L, _ = muscle_torque(act_shoulder_L)
tau_shoulder_R, _ = muscle_torque(act_shoulder_R)
tau_elbow_L, _ = muscle_torque(act_elbow_L)
tau_elbow_R, _ = muscle_torque(act_elbow_R)

# --- ATP drain per joint ---
atp_drain = sum(map(abs, [
    tau_hip_L, tau_hip_R, tau_knee_L, tau_knee_R,
    tau_ankle_L, tau_ankle_R, tau_shoulder_L, tau_shoulder_R,
    tau_elbow_L, tau_elbow_R
])) * 0.001
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
