# A7DO — Developmental Embodied Intelligence
## Master Specification & Mathematical Notebook

---

## 0. Purpose

A7DO is a **synthetic organism** that learns to act by **progressively solving gravity**.

It does not start with balance.
It does not start with walking.
It does not start with goals.

It starts with **motion**, **physics**, and **development**.

---

## 1. Core Principles (Non‑Negotiable)

1. Embodiment before cognition  
2. Physics before control  
3. Failure before optimisation  
4. Developmental order is mandatory  
5. One physics stack reused everywhere  
<BLOCKQUOTE><P>If a stage is skipped, later stages fail.</P></BLOCKQUOTE>

---

## 2. Mathematical Foundations

### 2.1 Gravity & Inverted Pendulum (Standing Core)

Torso dynamics:

\[
\ddot{\theta}_t
=
\frac{g}{l}\sin(\theta_t)
+
\frac{\tau_t}{I}
\]

Where:
- \( g \) = gravity
- \( l \) = COM height
- \( I \) = inertia
- \( \tau_t \) = net joint torque

If \( \tau_t = 0 \), the organism falls.

---

### 2.2 Centre of Mass (COM)

Minimal (torso‑dominant):

\[
x_{COM} = l \sin(\theta_t)
\]

Full multi‑link:

\[
x_{COM} = \frac{\sum m_i x_i}{\sum m_i}
\]

---

### 2.3 Base of Support (BOS)

Feet define stability:

\[
BOS = [x_L, x_R]
\]

Standing is possible only if:

\[
x_{COM} \in BOS
\]

---

### 2.4 Capture Point (Predictive Stability)

\[
x_{cp}
=
x_{COM}
+
\frac{\dot{x}_{COM}}{\omega_0}
\quad
\omega_0 = \sqrt{\frac{g}{l}}
\]

This predicts **where the body is going**, not where it is.

---

## 3. Muscle & Metabolism Model

### 3.1 Pull‑Only Muscle Force

\[
F = F_{max} \cdot a \cdot C_{fatigue}
\]

- \( a \in [0,1] \) activation
- muscles cannot push

---

### 3.2 Joint Torque from Muscles

\[
\tau = r (F_{agonist} - F_{antagonist})
\]

---

### 3.3 ATP & Fatigue

\[
C_{fatigue} = \frac{ATP_{current}}{ATP_{max}}
\]

Energy drain:

\[
\dot{ATP} = -k \sum |F|
\]

Fatigue scales *all* movement.

---

## 4. Developmental Ladder (Canonical Order)

Motor Noise → Kicking / Jerking → Rolling → Head Control → Sitting → Crawling → Kneeling → Kneeling Balance Reflex → Half‑Stand → Full Stand → Walk Initiation → Continuous Walking → Running


---

## 5. Stage 0 — Motor Noise (Babbling)

### 5.1 Neural Noise

\[
a_i(t) = \text{clip}(\eta_i(t), 0, 1)
\quad
\eta_i \sim \mathcal{N}(0,\sigma^2)
\]

No targets. No balance.

Purpose: discover limbs.

---

## 6. Stage 1 — Kicking & Jerking

Introduce oscillation:

\[
\dot{\phi}_i = \omega_i
\]

\[
a_i(t) = A_i \sin(\phi_i) + \eta_i(t)
\]

Produces kicks, flails, asymmetry.

---

## 7. Stage 2 — Rolling

Whole‑body torque:

\[
I_b \ddot{\Theta} = \sum r_i F_i - c\dot{\Theta}
\]

Rolling occurs when:

\[
|\tau| > \tau_{roll}
\]

Emergent, not planned.

---

## 8. Stage 3 — Head–Neck Control

### 8.1 Coupled Dynamics

Torso:
\[
I_t \ddot{\theta}_t
=
\frac{g}{l_t}\sin(\theta_t)
+
\tau_t
-
\tau_n
\]

Head:
\[
I_n \ddot{\theta}_n
=
\frac{g}{l_n}\sin(\theta_n)
+
\tau_n
\]

---

### 8.2 Neck Reflex

\[
\tau_n
=
K_{pn}(0-\theta_n)
+
K_{dn}(0-\dot{\theta}_n)
\]

Head stabilises *before* posture.

---

## 9. Stage 4 — Sitting

Orientation variable:

\[
\Theta \in [0,\pi]
\]

Target:

\[
\Theta \rightarrow \frac{\pi}{2}
\]

Arm support torque:

\[
\tau_{arm} = r_{arm} F_{arm}
\]

Pelvis becomes first anchor.

---

## 10. Stage 5 — Crawling

### 10.1 Support Set

\[
\mathcal{S} = \{H_L, H_R, K_L, K_R\}
\]

Stability:

\[
x_{COM} \in \text{ConvexHull}(\mathcal{S})
\]

No balance controller required.

---

### 10.2 Crawl Phase

\[
\dot{\phi} = \omega_{crawl}
\]

Contralateral pattern:
- RH → LK → LH → RK

---

## 11. Stage 6 — Kneeling

Support reduces:

\[
\mathcal{S} = \{K_L, K_R\}
\]

COM rises:

\[
z_{COM}^{kneel} > z_{COM}^{crawl}
\]

Introduce **proto‑balance**.

---

## 12. Stage 7 — Kneeling Balance Reflexes

Lateral dynamics:

\[
\ddot{y}_{COM}
=
\frac{g}{l_{kneel}}(y_{COM}-y_{knees})
\]

Reflex:

\[
\tau_{lat}
=
K_{p,lat}(0-\theta_{lat})
+
K_{d,lat}(0-\dot{\theta}_{lat})
\]

Arms rescue if needed.

---

## 13. Stage 8 — Half‑Stand

Unilateral support:

\[
\mathcal{S} = \{F_{stance}, K_{trail}\}
\]

Weight shift:

\[
x_{COM} \rightarrow x_{stance}
\]

Hip extension:

\[
\tau_{hip}
=
K_{p,h}(0-\theta_{hip})
+
K_{d,h}(0-\dot{\theta}_{hip})
\]

---

## 14. Stage 9 — Full Stand

Trailing knee unloads:

\[
F_{K_{trail}} < \epsilon
\]

Full inverted pendulum activates:

\[
\ddot{x}_{COM}
=
\frac{g}{l_{stand}}(x_{COM}-x_{foot})
\]

Ankle PD balance:

\[
\tau_{ankle}
=
K_p(x_{ref}-x_{COM})
+
K_d(0-\dot{x}_{COM})
\]

---

## 15. Standing Failure & Recovery

### 15.1 Detection

\[
x_{cp} \notin BOS
\]

---

### 15.2 Recovery Modes

- Sit‑back (low ATP)
- Step‑out (capture)
- Arm rescue (lateral)
- Controlled fall (last resort)

---

## 16. Walk Initiation

Intentional bias:

\[
x_{ref}^{walk}
=
x_{ref}^{stand}
+
\alpha \cdot BOS_{width}
\]

Capture exits BOS → step.

---

## 17. Continuous Walking Gait

Phase oscillator:

\[
\dot{\phi} = \omega_g
\]

Foot placement:

\[
x_{foot}^{new} = x_{cp}
\]

BOS updates every step.

Walking = repeated capture.

---

## 18. Running (Extension)

Add flight phase:

\[
\ddot{z}_{COM} = -g
\]

Leg spring (SLIP):

\[
F_{leg} = k(l_0-l)
\]

Running = walking + flight + elasticity.

---

## 19. Control Architecture Summary

- Same physics everywhere
- Same muscles everywhere
- Same energy constraints everywhere
- Only **conditions** change

---

## 20. What A7DO Is

A7DO is:
- an embodied developmental system
- physically grounded
- failure‑tolerant
- executable at every stage

A7DO is **not**:
- an RL policy
- an animation system
- a symbolic AI

---

## 21. Final Statement
<BLOCKQUOTE><P>**A7DO learns to act by progressively solving gravity,  </P></BLOCKQUOTE>
before it ever learns to think.**

This document is the canonical specification.

---
