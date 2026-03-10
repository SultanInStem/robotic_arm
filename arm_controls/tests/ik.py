import roboticstoolbox as rtb
from math import pi
import roboticstoolbox as rtb
from spatialmath import SE3

robot = rtb.DHRobot([
    rtb.RevoluteDH(d=0.162,  alpha=pi/2,  a=0,       offset=0),
    rtb.RevoluteDH(d=0,      alpha=0,     a=0.1364,  offset=pi/2),
    rtb.RevoluteDH(d=0,      alpha=0,     a=0.1205,  offset=0),
    rtb.RevoluteDH(d=0.083,  alpha=pi/2,  a=0,       offset=pi/2),
    rtb.RevoluteDH(d=0.083,  alpha=-pi/2, a=0,       offset=0),
    rtb.RevoluteDH(d=0.0666, alpha=0,     a=0,       offset=0),
], name="myCobot320")
# a is the lenght of each link 
# alpha is the angle between two joints 
# offset is a fixed angle added to the joint angle 
# before any movement. Used to correct for the fact 
# that the arm's physical zero position doesn't always 
# match the mathematical zero.

# Define target position (x, y, z in meters)
target = SE3(0.3, 0.1, 0.2)

# Solve IK using Levenberg-Marquardt
solution = robot.ik_LM(target)
angles = solution[0]
print("Joint angles (radians):", angles)

# Verify with FK
fk = robot.fkine(angles)
print("FK result:", fk.t)  # should match your target