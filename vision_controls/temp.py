from pymycobot import MyCobot320Socket
mc = MyCobot320Socket("192.168.10.2", 9000)
print(mc.get_angles())