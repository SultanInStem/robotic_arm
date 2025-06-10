import time
from pymycobot.mycobot import MyCobot
import paramiko ### paramiko is used to connect to the arm via ssh

# ---------------- Setup ----------------
mc = MyCobot('/dev/ttyAMA0', 115200)
mc.init_gripper()

IMG_CENTER_X = 320
IMG_CENTER_Y = 240
CENTER_TOLERANCE = 20

# Connection to NVIDIA
NVIDIA_HOST = "129.8.203.200" #change based on ifconfig of NVIDIA
NVIDIA_USER = "agxorin3"
NVIDIA_PASSWORD = "fresnostate"
COORD_FILE = "/home/agxorin3/Desktop/strawberry/strawberry_coords.txt"

# Starting/Deposit Angles
ready_angles = [-10, 25, 55, 0, -90, 0]
deposit_angles = [65, -90, 90, 45, -90, 0]


# clear the coords file 
# it makes sure that the robot focuses on one strawberry at a time
def clean_strawberry_coords():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(NVIDIA_HOST, username=NVIDIA_USER, password=NVIDIA_PASSWORD)

    sftp = ssh.open_sftp()
    try:
        with sftp.open(COORD_FILE, "w") as f:
            f.write("")
    except FileNotFoundError:
        pass

    sftp.close()
    ssh.close()


# ---------------- Utilities ----------------
# fetch coords from coords file
def fetch_strawberry_coords():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(NVIDIA_HOST, username=NVIDIA_USER, password=NVIDIA_PASSWORD)

    sftp = ssh.open_sftp()
    try:
        with sftp.open(COORD_FILE, "r") as f:
            coords = f.readlines()
    except FileNotFoundError:
        coords = []

    sftp.close()
    ssh.close()
    print("STRAWBERRY: ")
    print(coords)
    return coords

# get the first coord within coords
def get_straw_pos(coords):
    return coords.pop(0)

# Set arm to ready position
def go_to_ready():
    mc.send_angles(ready_angles, 50)
    time.sleep(2)
    mc.set_gripper_state(0, 80)  # Open gripper
    time.sleep(1)

# Set arm to deposit position
def deposit():
    mc.send_angles(deposit_angles, 40)
    time.sleep(4)
    mc.set_gripper_state(0, 60)  # Open gripper
    time.sleep(1)

# Adjust joints 
def calculate_z_adjustment(j2):
    """
    Adjust J3/J4 based on how close the strawberry is.
    Closer in Y (higher center_y) means it needs to go lower.
    """
    if j2 < 15:  # Close
        print(f"1")
        return +32, -32, -2
    elif (j2 > 15) and (j2 < 20):  # Mid
        print(f"2")
        return +34, -32, -7
    elif (j2 > 20) and (j2 < 25):  # Far
        print(f"3")
        return +34, -32, -2
    elif (j2 > 25) and (j2 < 30):  # Very far
        print(f"4")
        return +38, -34, -10
    elif (j2 > 30) and (j2 < 35):  # Very far
        print(f"5")
        return +36, -34, -10
    elif (j2 > 35) and (j2 < 40):  # Very far
        print(f"6")
        return +36, -34, -10    
    else:
        return +0, +0, -0


# ---------------- Main Loop ----------------
if __name__ == "__main__":
    lock = 1
    go_to_ready()

    while True:
        coords = fetch_strawberry_coords() ### comes from sb_detect_send_coords.py
        if not len(coords):
            print("No strawberries detected.")
            continue
        
        curr_pos = get_straw_pos(coords)
        
        try:
            # convert coords from string to int
            center_x, center_y = map(int, curr_pos.split())
        except Exception:
            continue
        print(f"Detected strawberry at X={center_x}, Y={center_y}")
        
        # ---------------- Centering ----------------
        #Get current joint states
        j1, j2, j3, j4, j5, j6 = mc.get_angles()
        
        # X-axis (left/right)
        if abs(center_x - IMG_CENTER_X) > CENTER_TOLERANCE:
            if center_x < IMG_CENTER_X:
                j1 += 2
                j6 += 2
                print("→ Adjusting Right")
            else:
                j1 -= 2
                j6 -= 2
                print("← Adjusting Left")    
        # Y-axis (forward/backward)
        if abs(center_y - IMG_CENTER_Y) > CENTER_TOLERANCE:
            if center_y < IMG_CENTER_Y:
                j2 -= 1
                j4 -= 3
                print("↑ Moving Forward")
            else:
                j2 += 1
                j4 += 3
                print("↓ Moving Backward")

        # If not centered, update and continue
        if abs(center_x - IMG_CENTER_X) > CENTER_TOLERANCE or abs(center_y - IMG_CENTER_Y) > CENTER_TOLERANCE:
            mc.send_angles([j1, j2, j3, j4, -90, j6], 60)
            continue

        # ---------------- Picking ----------------
        print("✓ Strawberry Centered - Picking...")

        z_j2_offset, z_j3_offset, z_j4_offset = calculate_z_adjustment(j2)
        j2 += z_j2_offset
        j3 += z_j3_offset
        j4 += z_j4_offset
            
        mc.send_angles([j1, j2, j3, j4, -90, j6], 40)
        time.sleep(1.5)

        # Close gripper to pick
        mc.set_gripper_state(1, 40)
        time.sleep(1)
    
        # Deposit and reset
        deposit()
        clean_strawberry_coords()
        go_to_ready()
