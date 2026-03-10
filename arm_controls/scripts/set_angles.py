import sys
import os
sys.path.append(os.path.abspath(".."))
from commands.main import set_arms_angles
a1 = float(input("Enter a1 in radians: "))
a2 = float(input("Enter a2 in radians: "))
a3 = float(input("Enter a3 in radians: "))
a4 = float(input("Enter a4 in radians: "))
a5 = float(input("Enter a5 in radians: "))
a6 = float(input("Enter a6 in radians: "))
speed = int(input("Enter speed from 0 to 100: "))
set_arms_angles([a1,a2,a3,a4,a5,a6], speed)
