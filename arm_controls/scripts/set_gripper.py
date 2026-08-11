import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from commands.main import set_gripper
value = int(input("Enter value: 0=closed, 100=open "))
if value <= 100 and value >=0:
    set_gripper(value)
else: 
    print("Bruh")