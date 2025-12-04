
## How To Start Up The Arm
1) Open the gripper to the full extent 
2) Power on the arm 
3) Run reset.py to calibrate the arm 

Pymycobot (3.6.1 DO NOT UPDATE)



to transfrom a vector from end_effector_frame to base_frame, 
we shoud multiply the vector by a rotation matrix 




# Connecting ssh via ethernet 
sudo nmcli con delete static-eth0
sudo nmcli con add type ethernet ifname enp1s0 con-name static-eth0 ip4 192.168.10.1/24
sudo nmcli con up static-eth0

wget https://github.com/agraham56/Brandy/releases/download/v1.24/matrixbrandy_1.24_armhf.deb
sudo apt update
sudo apt install ./matrixbrandy_1.24_armhf.deb  