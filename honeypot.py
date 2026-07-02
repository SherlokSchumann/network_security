# create a TCP server and listen for incoming connections.
# If connected, send a message to the client and close the connection.
# Handle Multiple Connections using threading.

import socket
import threading
import selectors
from datetime import datetime
from time import sleep
import sys
import subprocess
import os

#======== Global Variables ========

HOST = "0.0.0.0" # Use the hosts IP address on all interfaces
PORT = 22

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# This is specific to the legacy telnet connection
telnet = False
IAC = bytes([255])
WILL = bytes([251])
WONT = bytes([252])
ECHO = bytes([1])

ssh_version_banner = b"SSH-2.0-OpenSSH_10.0p1-7+deb13u1\r\n"
password_prompt = b"debian@admin_machine.local's password: "
error_prompt = b"Permission denied, please try again.\n"

# not used yet
terminal_prompt = b"debian@admin_machine.local:~$ "


#====== Analyze logs ========

# moved to another file



#===== detect telnet or nc ========

def detectClient(conn, timeout=5):
    conn.settimeout(timeout)
    try:
        data = conn.recv(1024, socket.MSG_PEEK)
        if data and data[0] == 255:
            telnet = True
        else:
            telnet = False
    except socket.timeout:
        telnet = False
    finally:
        conn.settimeout(None)







#======= Recv Line Function =======
def recv_line(conn):
    buffer = b""
    while b"\n" not in buffer and b"\r" not in buffer:
        chunk = conn.recv(1)
        if not chunk:
            return None
        buffer += chunk
    return buffer 



#======== Client Handler ==========
def handle_client(conn, addr):

    log_path = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{addr[0]}_{addr[1]}.txt")
    with conn, open(log_path, "w") as log_file:

        try:

            # Write the initial log
            # attacker with this IP has connected at this time
            print(f"[*] Connected by {addr}")
            log_file.write(f"{datetime.now()}: [*] Connected by {addr}\n")

            # Simulate initial messages and log client output
            conn.sendall(ssh_version_banner)
            sleep(1.5)
            conn.sendall(b"The authenticity of this host can't be established.\nED25519 key fingerprint is SHA256:ZY+TYiOqb3kGRTbgUi6vQlZeyz9TCusKVblioBcevvE.")
            conn.sendall(b"\nAre you sure you want to continue connecting (yes/no/[fingerprint])? ")
            
            # We expect a reply from the user 
            data = recv_line(conn)

            # Suppose the attacker voluntarily closes the connection.
            if not data:
                print(f"[*] No data received from {addr}. Closing connection.")
                log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                parent_log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                conn.close()
                return


            user_response = data.decode(errors='ignore').strip().lower()
            print(f"[*] Received data from {addr}: {user_response}")
            log_file.write(f"{datetime.now()}: [*] Received data from {addr}: {user_response}\n")


            while True:
                if(user_response == "yes"):
                    sleep(1)
                    conn.sendall(b"Warning: Permanently added '' (ED25519) to the list of known hosts.\n")
                    log_file.write(f"{datetime.now()}: [*] {addr} will continue connecting.\n")
                    break
                elif(user_response == "no"):
                    conn.sendall(b"Host key verification failed.\n")
                    # Write closing time to parent log file
                    parent_log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection by saying no.\n")
                    conn.close()
                    return
                else:
                    conn.sendall(b"Please type 'yes' or 'no': ")
                    data = recv_line(conn)

                    if not data:
                        print(f"[*] No data received from {addr}. Closing connection.")
                        log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                        parent_log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                        conn.close()
                        return

                    user_response = data.decode(errors='ignore').strip().lower()
                    print(f"[*] Received data from {addr}: {user_response}")
                    log_file.write(f"{datetime.now()}: [*] Received data from {addr}: {user_response}\n")
                
            i = 0
            while i < 6:
                conn.sendall(password_prompt)
                if telnet:
                    conn.sendall(IAC + WILL + ECHO)
                password = recv_line(conn)

                if telnet:
                    conn.sendall(IAC + WONT + ECHO)

                if not password:
                    print(f"[*] No password recieved from {addr}. Closing connection.")
                    log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                    parent_log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                    conn.close()
                    return

                log_file.write(f"{datetime.now()}: [*] Received password from {addr}: {password.decode(errors='ignore')}\n")
                sleep(2)
                conn.sendall(error_prompt)
                i = i + 1

            # After exiting the loop
            conn.sendall(b"maximum number of attempts exceeded\n")
            log_file.write(f"{datetime.now()}: [*] {addr} has exceeded the maximum number of attempts. Closing connection\n")
            parent_log_file.write(f"{datetime.now()}: [*] {addr} has exceeded the maximum number of attempts. Closing connection\n")
            conn.close()
        

        # Catch the exceptions and log what is necessary.
        except (ConnectionResetError, ConnectionAbortedError) as e:
            print(f"[*] Connection with {addr} was closed unexpectedly: {e}")
            log_file.write(f"{datetime.now()}: [*] Connection with {addr} was closed unexpectedly: {e}\n")
            parent_log_file.write(f"{datetime.now()}: [*] Connection with {addr} was closed unexpectedly: {e}\n")

        except Exception as e:
            print(f"[*] An unexpectederror occurred with {addr}: {e}")
            log_file.write(f"{datetime.now()}: [*] An error occurred with {addr}: {e}\n")
            parent_log_file.write(f"{datetime.now()}: [*] An error occurred with {addr}: {e}\n")
        
        finally:
            if conn:
                conn.close()
            if log_file:
                log_file.write(f"{datetime.now()}: [*] Connection with {addr} closed.\n")
                parent_log_file.write(f"{datetime.now()}: [*] Connection with {addr} closed.\n")
                log_file.close()
    
    return
            




with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    parent_log_path = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_parent_log.txt")
    with open(parent_log_path, "w") as parent_log_file:
                       
        s.bind((HOST, PORT))
        s.listen()
        print(f"[*] Listening on {HOST}:{PORT}")
        parent_log_file.write(f"{datetime.now()}: [*] Listening on {HOST}:{PORT}\n")
        
        try:
        
            while True:
                conn, addr = s.accept()
                detectClient(conn)
                parent_log_file.write(f"{datetime.now()}: [*] Accepted connection from {addr}\n")
                threading.Thread(target=handle_client, args=(conn, addr)).start()
        except KeyboardInterrupt:
            print("\n[!] Sever shutting down. Starting Analysis...")
            sleep(1.5)
            subprocess.run([sys.executable, "analyze-logs.py"])

            sys.exit(0)
        
