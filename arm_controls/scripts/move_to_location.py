import sys
import os
sys.path.append(os.path.abspath(".."))
from commands.main import move_to_location
x = float(input("Enter x in meters: "))
y = float(input("Enter y in meters: "))
z = float(input("Enter z in meters: "))
speed = int(input("Enter speed from 0 to 100: "))
move_to_location([x,y,z], speed)
