import sys
import os
import time
from pymycobot.mycobot320 import MyCobot320
sys.path.append(os.path.abspath(".."))
from commands.main import reset, move_to_location, close_gripper, open_gripper
from utils.funcs import compute_ik, compute_fk, convert_to_radians, convert_point_from_end_effector_to_base_frame
from utils.globals import PORT, BANDWIDTH
mc = MyCobot320(PORT, BANDWIDTH)

# reset()
# move_to_location([0.3, 0, 0.4], 20) ### go to ready position 
while True: 
    # FETCH COORDINATES FROM THE FILE
    filename = "../../vision_controls/AI_model/coords_data.txt"
    coords_in_end_effector_frame = []

    try:
        with open(filename, 'r') as f:
            # 1. Read the first line of the file
            line = f.readline()
            
            # 2. Split the line into a list of strings
            #    This gives: ['10', ' 20', ' 30', ' 40', ' 50\n']
            string_list = line.split(',')
            
            # 3. Loop through, clean up, and convert to numbers
            for item in string_list:
                # item.strip() removes extra spaces and newlines
                # int() converts the clean string to a number
                number = float(item.strip())
                coords_in_end_effector_frame.append(number)
                
        print(f"Successfully read file '{filename}'")
        print(f"Here is your list of numbers: {coords_in_end_effector_frame}")

    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    
    if len(coords_in_end_effector_frame) == 3:
        coords_in_end_effector_frame.append(1)
        current_angles = [0] + mc.get_angles() + [0]
        for i in range(0, len(current_angles)): 
            current_angles[i] = convert_to_radians(current_angles[i])
        print("Current angles: ", current_angles)
        point = convert_point_from_end_effector_to_base_frame(coords_in_end_effector_frame, current_angles)
        print("Point in base frame: ", point)



