# Important Instructions To Read !!! 

## How To Start Up The Arm
1) Open the gripper to the full extent 
2) Power on the arm 
3) Run reset.py to calibrate the arm 

## DONT'S 
- DO NOT disconnect ANY wires while the arm is still on. 
- DO NOT connect wires loosely. Always make sure they are secured tightly. 
- DO NOT touch the arm while it is on. Power it off and they do what you want.
- DO NOT update pymycobot package. 
- DO NOT touch colcon_ws file. 
- DO NOT update the version of ROS2. 
- DO NOT update the version of C++. 
- DO NOT update the version of Python. 


# Packages and their functions
## Paramiko 
Paramiko package is used to establish SSH connections to remote devices. In this case, the robotic arm. 
## Pymycobot (3.6.1 DO NOT UPDATE)
Pymycobot is designed to control MyCobot robotic arms developed by Elephant Robotics. It controls the movement of joints and grippers. 
## ikpy 
ikpy is used to implement inverse kinematics and compute all joint angles at once.
