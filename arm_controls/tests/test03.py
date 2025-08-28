# coding=utf-8
from pymycobot import MyCobot320
import time
from pymycobot import __version__

print(__version__)

# Initialize robot arm connection (modify serial port according to actual situation)
mc = MyCobot320('/dev/ttyAMA0', 115200, debug=False)
#mc = MyCobot320('/dev/ttyAMA0', 115200, debug=True) #If the return value is -1 or None, open this line of code to run
coords = mc.get_coords()
time.sleep(0.1)
print(coords)

def io_mode_test():
    """IO mode test: Control gripper to open and close 3 times"""
    print("Starting IO mode test...")
    mc.set_gripper_mode(1)  # Set to IO mode
    for i in range(3):
        print(f"Cycle {i+1}")
        mc.set_digital_output(1, 0)  # Set IO to low level
        time.sleep(1)
        mc.set_digital_output(1, 1)
        time.sleep(1)
        mc.set_digital_output(2, 0)  # Close gripper
        time.sleep(1)
        mc.set_digital_output(2, 1)  # Restore IO to low level
        time.sleep(1)
    print("IO mode test completed")

def transmission_mode_test():
    """Transmission mode test: Control gripper to open and close 3 times"""
    print("Starting transmission mode test...")
    mc.set_gripper_mode(0)  # Set to transmission mode
    time.sleep(1)
    for i in range(3):
        print(f"Cycle {i+1}")
        mc.set_gripper_value(26, 20)  # Close gripper (adjust value according to actual calibration)
        time.sleep(1)
        mc.set_gripper_value(86, 20)  # Open gripper (adjust value according to actual calibration)
        time.sleep(1)
    print("Transmission mode test completed")

def calibrate_gripper():
    """Calibrate the gripper"""
    print("Starting gripper calibration...")
    mc.release_all_servos()
    print("Please manually open the gripper to maximum position within 5 seconds")
    time.sleep(5)
    mc.power_on()
    mc.set_gripper_mode(0)  # Use transmission mode for calibration
    time.sleep(1)
    mc.set_gripper_calibration()
    print("Gripper calibration successful!")

def gripper_data_read():
    print("零位矫正前当前所在位置: ", mc.get_encoder(7))
    time.sleep(0.1)
    mc.set_gripper_calibration()
    time.sleep(0.1)
    print("零位矫正后当前所在位置（矫正成功夹爪会锁住，并且位置接近100）: ", mc.get_encoder(7))
    time.sleep(0.1)
    print("开始夹爪参数更新...")
    # datas = [10, 0, 1, 150]
    datas = [25, 25, 0, 140]
    address = [21, 22, 23, 16]
    current_datas = []
    new_datas = []
    for addr in address:
        current_datas.append(mc.get_servo_data(7, addr))
        time.sleep(0.1)
    print("当前夹爪参数为: ", current_datas)
    for addr in range(len(address)):
        mc.set_servo_data(7, address[addr], datas[addr])
        time.sleep(0.1)
    for addr in address:
        new_datas.append(mc.get_servo_data(7, addr))
        time.sleep(0.1)
    print("更新后夹爪参数为: ", new_datas)


def robot_arm_data():
    robot_coods = mc.get_coords()
    time.sleep(0.1)
    print("robot coords:", str(robot_coods))
    
    atom_version = mc.get_atom_version()
    time.sleep(0.2)
    print("atom version: ",str(atom_version))

    system_version = mc.get_system_version()
    time.sleep(0.1)
    print("system version: ", str(system_version))

    basic_version = mc.get_basic_version()
    time.sleep(0.1)
    print("basic version:", str(basic_version))

    error_info = mc.get_error_information()
    time.sleep(0.1)
    print("read error: ", str(error_info))

    next_error = mc.read_next_error()
    time.sleep(0.1)
    print("read next error: ", str(error_info))



def Joints_data():
    with open('output.txt', 'w') as file:
        version = __version__
        file.write("pymycobot-Version:" + str(version) + " \n ")
        
        # 写入Atom版本信息
        # Writes the Atom version information
        atom_version = mc.get_atom_version()
        file.write("atom version: " + str(atom_version) + "\n")
        time.sleep(0.1)
        
        # 写入系统版本信息
        # Writes the system version information
        system_version = mc.get_system_version()
        file.write("system version: " + str(system_version) + "\n")
        time.sleep(0.1)

        # 写入基础版本信息
        # Writes the base version information
        basic_version = mc.get_basic_version()
        file.write("basic version: " + str(basic_version) + "\n")
        time.sleep(0.1)

        # 写入错误信息
        # Write error message
        error_info = mc.get_error_information()
        file.write("error information: " + str(error_info) + "\n")
        time.sleep(0.1)

        # 写入下一个错误信息
        # Write the next error message
        next_error = mc.read_next_error()
        file.write("read next error: " + str(next_error) + "\n")
        time.sleep(0.1)

        # 循环写入每个关节的数据
        # Write data to each joint in a loop
        for i in range(1, 7):
            print("servo_enabled" + str(i) + "write")
            servo_data_22 = mc.is_servo_enable(i)
            file.write("[" + str(i) + "]" + str(servo_data_22))

        for i in range(1, 7):
            print("Servo " + str(i) + "write")
            for j in range(0, 89):
                servo_data_21 = mc.get_servo_data(i, j)
                file.write("[" + str(j) + "]" + str(servo_data_21))
            file.write("\n")

def main():
    print("try restarting the robotic arm or confirming whether the robotic arm joint is locked. Atom will be green")
    print("If the return value is -1 or None, enable debug=True in the code and comment debug= False.")
    print("Gripper Control Script")
    print("1: Run IO mode test (When switching from the transparent transmission mode to the IO mode, the gripper needs to be de-energized and reconnected.)")
    print("2: Run transmission mode test")
    print("3: Perform gripper calibration")
    print("4: Obtain and calibrate gripper parameters ")
    print("5: Robotic Arm Parameter Acquisition ")
    print("6: Acquisition of Robotic Arm Joint Information (output output.txt in the same directory)")
    print("0: Exit program")
    
    while True:
        try:
            choice = input("Please enter operation number (0-3): ")
            if choice == '1':
                io_mode_test()
            elif choice == '2':
                transmission_mode_test()
            elif choice == '3':
                calibrate_gripper()
            elif choice == "4":
                gripper_data_read()
            elif choice == "5":
                robot_arm_data()
            elif choice == "6":
                Joints_data()
            elif choice == '0':
                print("Program exiting")
                break
            else:
                print("Invalid input, please enter a number between 0-6")
        except Exception as e:
            print(f"Operation error: {e}")
            break

main()