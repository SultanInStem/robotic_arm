import time
import os
import sys
import numpy as np
from pymycobot.mycobot import MyCobot
from pymycobot.genre import Angle, Coord
import RPi.GPIO as GPIO

resetAngles = [0,0,0,0,0,0] #set arm back to normal
Angles1 = [(-10),25,55,0,(-90),0] #ready for coords pos
picking = [(-10),70,10,0,(-90),0] #modify for straw detection
deposit = [65, -90, 90, 45, -90, 0]

mc = MyCobot('/dev/ttyAMA0', 115200)
def starting_pos():
    #mc.send_angles(resetAngles, 30)
    time.sleep(1)
    mc.send_angles(Angles1, 30)
    time.sleep(1)
    mc.set_gripper_state(0, 100) #open end effector
    time.sleep(1)
    #ref = mc.get_world_reference()
    #print(f"{ref}")
    
def pick_straw():
    mc.send_angles(picking, 20)
    time.sleep(1)
    mc.set_gripper_state(1, 40) #close end effector
    
def deposit_straw():
    mc.send_angles(deposit, 50)
    time.sleep(3)
    mc.set_gripper_state(0, 100) #open end effector
    time.sleep(1)
    
starting_pos()
#time.sleep(6)
#pick_straw()
#time.sleep(2)
#deposit_straw()
#time.sleep(2)
#starting_pos()
#time.sleep(6)
