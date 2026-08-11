import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from commands.main import close_gripper
value = int(input("Enter extent of the closure (0-100) "))
if value <= 100 and value >=0:
    close_gripper()
else: 
    print("Bruh")