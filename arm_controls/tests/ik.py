import roboticstoolbox as rtb
from math import pi
import numpy as np
import matplotlib.pyplot as plt
from spatialmath import SE3

# ── Robot definition ──────────────────────────────────────────────────────────
robot = rtb.DHRobot([
    rtb.RevoluteDH(d=0.1739,  alpha=pi/2,  a=0,      offset=0),      # J1
    rtb.RevoluteDH(d=0,       alpha=0,     a=0.135,  offset=pi/2),   # J2
    rtb.RevoluteDH(d=0,       alpha=0,     a=0.120,  offset=0),      # J3
    rtb.RevoluteDH(d=0.08878, alpha=pi/2,  a=0,      offset=pi/2),   # J4
    rtb.RevoluteDH(d=0.095,   alpha=-pi/2, a=0,      offset=0),      # J5
    rtb.RevoluteDH(d=0.0655,  alpha=0,     a=0,      offset=0),      # J6
], name="myCobot320")

# ── Sampling ──────────────────────────────────────────────────────────────────
ARM_LENGTH = 0.5       # m — total reach of your arm
N_TARGETS  = 200
np.random.seed(42)

# Sample uniformly inside a sphere of radius ARM_LENGTH
def sample_sphere(radius, n):
    points = []
    while len(points) < n:
        p = np.random.uniform(-radius, radius, 3)
        if np.linalg.norm(p) <= radius:
            points.append(p)
    return np.array(points)

targets = sample_sphere(ARM_LENGTH, N_TARGETS)

# ── Evaluate IK over all targets ──────────────────────────────────────────────
errors      = []
converged   = []

for idx, xyz in enumerate(targets):
    target   = SE3(float(xyz[0]), float(xyz[1]), float(xyz[2]))

    # ik_LM returns (q, success, iterations, searches, residual)
    solution = robot.ik_LM(target)
    q        = solution[0]
    success  = solution[1]          # True if converged

    # Compute actual FK error regardless of success flag
    fk_result = robot.fkine(q)
    err       = np.linalg.norm(fk_result.t - xyz)

    errors.append(err)
    converged.append(bool(success))

    if (idx + 1) % 50 == 0:
        print(f"  Processed {idx+1}/{N_TARGETS} targets...")

errors    = np.array(errors)
converged = np.array(converged)

# ── Print statistics ──────────────────────────────────────────────────────────
print("\n── Results ───────────────────────────────────────────")
print(f"  Targets evaluated   : {N_TARGETS}")
print(f"  Converged           : {converged.sum()} / {N_TARGETS}  ({100*converged.mean():.1f}%)")
print(f"  Mean position error : {errors.mean()*1000:.4f} mm")
print(f"  Std position error  : {errors.std()*1000:.4f} mm")
print(f"  Max position error  : {errors.max()*1000:.4f} mm")
print(f"  Min position error  : {errors.min()*1000:.4f} mm")
print("──────────────────────────────────────────────────────")

# ── Plot 1: Error histogram ───────────────────────────────────────────────────
fig1, ax1 = plt.subplots(figsize=(7, 4))
ax1.hist(errors * 1000, bins=30, color='steelblue', edgecolor='white', linewidth=0.5)
ax1.axvline(errors.mean() * 1000, color='red', linestyle='--', linewidth=1.8,
            label=f'Mean = {errors.mean()*1000:.4f} mm')
ax1.set_xlabel("Final position error (mm)", fontsize=13)
ax1.set_ylabel("Count", fontsize=13)
ax1.set_title(f"IK Position Error over {N_TARGETS} Random Targets  "
              f"(workspace radius = {ARM_LENGTH} m)", fontsize=12)
ax1.legend(fontsize=11)
ax1.grid(True, alpha=0.3)
fig1.tight_layout()
fig1.savefig("error_histogram.png", dpi=150)
print("Saved error_histogram.png")

# ── Plot 2: 3D workspace error map ────────────────────────────────────────────
fig2 = plt.figure(figsize=(7, 6))
ax2  = fig2.add_subplot(111, projection='3d')
sc   = ax2.scatter(targets[:, 0], targets[:, 1], targets[:, 2],
                   c=errors * 1000, cmap='plasma', s=18, alpha=0.8)
plt.colorbar(sc, ax=ax2, label='Position error (mm)', shrink=0.6)
ax2.set_xlabel('X (m)', fontsize=11)
ax2.set_ylabel('Y (m)', fontsize=11)
ax2.set_zlabel('Z (m)', fontsize=11)
ax2.set_title('IK Error Distribution across Workspace', fontsize=13)
fig2.tight_layout()
fig2.savefig("workspace_error_map.png", dpi=150)
print("Saved workspace_error_map.png")