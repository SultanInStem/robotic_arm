import sys
import os
from pymycobot.mycobot import MyCobot 
sys.path.append(os.path.abspath(".."))
from utils.compute_ik import compute_ik
from utils.globals import PORT, BANDWIDTH

mc = MyCobot(PORT, BANDWIDTH)


compute_ik(0,0,0.5)