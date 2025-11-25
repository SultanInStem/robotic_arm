import socket

# --- Configuration ---
HOST = '0.0.0.0'  # Listen on all available network interfaces
PORT = 65432        # A port to listen on (must match the client)
BUFFER_SIZE = 4096  # 4KB buffer for receiving data
RECEIVED_FILENAME = 'coords_data.txt' # Name to save the file as
# ---------------------

print("--- Raspberry Pi File Receiver (Socket) ---")
print(f"Listening on {HOST}:{PORT}")

# 1. Create a socket object (AF_INET = IPv4, SOCK_STREAM = TCP)
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # 2. Bind the socket to the host and port
        s.bind((HOST, PORT))
        
        # 3. Enable the server to accept connections
        s.listen()
        
        # 4. Loop forever to accept new connections
        while True:
            print(f"\nWaiting for a connection...")
            try:
                # conn = new socket for this specific client
                # addr = address of the client (Jetson)
                conn, addr = s.accept()
                
                # Use 'with' to auto-close the connection when done
                with conn:
                    print(f"Connected by {addr}")
                    
                    # 5. Open a new file in 'write binary' (wb) mode
                    with open(RECEIVED_FILENAME, 'wb') as f:
                        while True:
                            # 6. Receive data in chunks
                            data = conn.recv(BUFFER_SIZE)
                            
                            # If recv() returns an empty bytes object (b''),
                            # it means the client has closed the connection.
                            if not data:
                                break
                            
                            # 7. Write the data chunk to the file
                            f.write(data)
                            
                    print(f"Successfully received file and saved as {RECEIVED_FILENAME}")

            except Exception as e:
                print(f"Error during connection: {e}")

except socket.error as e:
    print(f"Socket error: {e}")
except Exception as e:
    print(f"Error setting up server: {e}")