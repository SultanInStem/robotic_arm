
## How To Start Up The Arm
1) Open the gripper to the full extent 
2) Power on the arm 
3) Run reset.py to calibrate the arm 

wget https://sourceforge.net/projects/bwbasic/files/bwbasic/version%202.40/bwbasic-2.40.zip





## Other 

### current_location.txt 
The purpose of this file is to help us avoid using the get_position() method provided by mycobot library. It contains the current position of the arm. The reason is that it returns completely incorrect positions.

### mycobot_320pi.urdf