import socket
import time
import os

# --- Configuration ---
# !!! IMPORTANT !!!
# Change this to the IP address of your Raspberry Pi
SERVER_HOST = '192.168.10.2' # Example: '192.168.1.10'
SERVER_PORT = 65432          # Must match the port on the server
BUFFER_SIZE = 4096           # 4KB buffer for sending data
# ---------------------

LOCAL_FILE = 'coords_data.txt'

print("--- Jetson File Sender (Socket) ---")

# --- 1. Create the .txt file ---
print(f"Creating local file: {LOCAL_FILE}")
try:
    with open(LOCAL_FILE, 'w') as f:
        f.write("This is a test file from the Jetson.\n")
        f.write(f"Timestamp: {time.time()}\n")
        f.write("Hello, Raspberry Pi! (via Socket)\n")
    print("Local file created successfully.")
except Exception as e:
    print(f"Error creating file: {e}")
    exit()

# --- 2. Send the file ---
print(f"Connecting to Raspberry Pi at {SERVER_HOST}:{SERVER_PORT}...")
try:
    # 1. Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
        # 2. Connect to the server
        s.connect((SERVER_HOST, SERVER_PORT))
        print("Connected.")
        
        # 3. Open the file in 'read binary' (rb) mode
        with open(LOCAL_FILE, 'rb') as f:
            while True:
                # 4. Read a chunk of data from the file
                bytes_read = f.read(BUFFER_SIZE)
                
                # If we're at the end of the file, bytes_read will be empty
                if not bytes_read:
                    break
                
                # 5. Send the data chunk to the server
                s.sendall(bytes_read)
                
        # 6. The 'with' block will auto-close the connection here
        print(f"File '{LOCAL_FILE}' sent successfully.")

except socket.error as e:
    print(f"Socket error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

# Optional: Clean up the local file
# if os.path.exists(LOCAL_FILE):
#     os.remove(LOCAL_FILE)
#     print(f"Cleaned up local file: {LOCAL_FILE}")

print("Jetson script finished.")