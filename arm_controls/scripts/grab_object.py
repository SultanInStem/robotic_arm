import sys
import os
sys.path.append(os.path.abspath(".."))
from commands.main import grab_object
degree = int(input("Enter gripper degree (0-100): "))
grab_object(80, degree)