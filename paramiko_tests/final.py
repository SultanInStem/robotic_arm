import time
from pymycobot.mycobot import MyCobot
import paramiko

# ---------------- Setup ----------------
mc = MyCobot('/dev/ttyAMA0', 115200)

IMG_CENTER_X = 320
IMG_CENTER_Y = 240
CENTER_TOLERANCE = 20

# Connection to NVIDIA
NVIDIA_HOST = import time
from pymycobot.mycobot import MyCobot
import paramiko

# ---------------- Setup ----------------
mc = MyCobot('/dev/ttyAMA0', 115200)

IMG_CENTER_X = 320
IMG_CENTER_Y = 240
CENTER_TOLERANCE = 20

# Connection to NVIDIA
NVIDIA_HOST = "129.8.203.200"
NVIDIA_USER = "agxorin3"
NVIDIA_PASSWORD = "fresnostate"
COORD_FILE = "/home/agxorin3/Desktop/strawberry/strawberry_coords.txt"

# Starting/Deposit Angles
ready_angles = [-10, 25, 55, 0, -90, 0]
deposit_angles = [65, -90, 90, 45, -90, 0]

# ---------------- Utilities ----------------
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
    return coords

def go_to_ready():
    mc.send_angles(ready_angles, 30)
    time.sleep(2)
    mc.set_gripper_state(0, 80)  # Open gripper
    time.sleep(1)

def deposit():
    mc.send_angles(deposit_angles, 30)
    time.sleep(3)
    mc.set_gripper_state(0, 60)  # Open gripper
    time.sleep(1)

def calculate_z_adjustment(j2_value):
    """
    Adjust J3/J4 based on how close the strawberry is.
    Closer in Y (higher center_y) means it needs to go lower.
    """
    if j2_value < 0:  # Close
        print(f"1")
        return +14, -14, +0
    elif (j2_value > 0) and (j2_value < 10):  # Mid
        print(f"2")
        return +19, -19, -2
    elif (j2_value > 10) and (j2_value < 20):  # Far
        print(f"3")
        return +24, -24, -5
    elif (j2_value > 20) and (j2_value < 30):  # Very far
        print(f"4")
        return +37, -37, -7
    elif (j2_value > 30) and (j2_value < 40):  # Very far
        print(f"5")
        return +34, -34, -9
    elif (j2_value > 40) and (j2_value < 50):  # Very far
        print(f"6")
        return +39, -39, -12    
    else:
        return +0, +0, -0

# ---------------- Main Loop ----------------
go_to_ready()

while True:
    coords = fetch_strawberry_coords()
    if not coords:
        print("No strawberries detected.")
        continue
    curr_pos = multi_straw(coords)
    for line in coords:
        try:
            center_x, center_y = map(int, line.split())
        except ValueError:
            continue

        print(f"Detected strawberry at X={center_x}, Y={center_y}")

        # Get current joint states
        j1, j2, j3, j4, j5, j6 = mc.get_angles()

        # ---------------- Centering ----------------
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
            mc.send_angles([j1, j2, j3, j4, -90, j6], 40)
            #time.sleep(0.4)
            continue

        # ---------------- Picking ----------------
        print("✓ Strawberry Centered - Picking...")

        z_j2_offset, z_j3_offset, z_j4_offset = calculate_z_adjustment(j2)
        j2 += z_j2_offset
        j3 += z_j3_offset
        j4 += z_j4_offset
        
        #j4 = max(min(j4, 10), -15)

        mc.send_angles([j1, j2, j3, j4, -90, j6], 40)
        time.sleep(1.5)

        # Close gripper to pick
        mc.set_gripper_state(1, 40)
        time.sleep(1)

        # Deposit and reset
        deposit()
        go_to_ready()
        
        break
NVIDIA_USER = "agxorin3"
NVIDIA_PASSWORD = "fresnostate"
COORD_FILE = "/home/agxorin3/Desktop/strawberry/strawberry_coords.txt"

# Starting/Deposit Angles
ready_angles = [-10, 25, 55, 0, -90, 0]
deposit_angles = [65, -90, 90, 45, -90, 0]

# ---------------- Utilities ----------------
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
    return coords

def go_to_ready():
    mc.send_angles(ready_angles, 30)
    time.sleep(2)
    mc.set_gripper_state(0, 80)  # Open gripper
    time.sleep(1)

def deposit():
    mc.send_angles(deposit_angles, 30)
    time.sleep(3)
    mc.set_gripper_state(0, 60)  # Open gripper
    time.sleep(1)

def calculate_z_adjustment(j2_value):
    """
    Adjust J3/J4 based on how close the strawberry is.
    Closer in Y (higher center_y) means it needs to go lower.
    """
    if j2_value < 0:  # Close
        print(f"1")
        return +14, -14, +0
    elif (j2_value > 0) and (j2_value < 10):  # Mid
        print(f"2")
        return +19, -19, -2
    elif (j2_value > 10) and (j2_value < 20):  # Far
        print(f"3")
        return +24, -24, -5
    elif (j2_value > 20) and (j2_value < 30):  # Very far
        print(f"4")
        return +37, -37, -7
    elif (j2_value > 30) and (j2_value < 40):  # Very far
        print(f"5")
        return +34, -34, -9
    elif (j2_value > 40) and (j2_value < 50):  # Very far
        print(f"6")
        return +39, -39, -12    
    else:
        return +0, +0, -0

# ---------------- Main Loop ----------------
go_to_ready()

while True:
    coords = fetch_strawberry_coords()
    if not coords:
        print("No strawberries detected.")
        continue

    for line in coords:
        try:
            center_x, center_y = map(int, line.split())
        except ValueError:
            continue

        print(f"Detected strawberry at X={center_x}, Y={center_y}")

        # Get current joint states
        j1, j2, j3, j4, j5, j6 = mc.get_angles()

        # ---------------- Centering ----------------
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
            mc.send_angles([j1, j2, j3, j4, -90, j6], 40)
            #time.sleep(0.4)
            continue

        # ---------------- Picking ----------------
        print("✓ Strawberry Centered - Picking...")

        z_j2_offset, z_j3_offset, z_j4_offset = calculate_z_adjustment(j2)
        j2 += z_j2_offset
        j3 += z_j3_offset
        j4 += z_j4_offset
        
        #j4 = max(min(j4, 10), -15)

        mc.send_angles([j1, j2, j3, j4, -90, j6], 40)
        time.sleep(1.5)

        # Close gripper to pick
        mc.set_gripper_state(1, 40)
        time.sleep(1)

        # Deposit and reset
        deposit()
        go_to_ready()
        break
