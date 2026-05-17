# joints.py
def default_joints():
    return {
        "angles": {
            "hip": 0.0, "knee": 0.0, "ankle": 0.0,
            "shoulder": 0.0, "elbow": 0.0
        }
    }

def joint_torque(moment_arm, F_agonist, F_antagonist):
    return moment_arm * (F_agonist - F_antagonist)
