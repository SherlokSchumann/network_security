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


#======== FTP Client Handler (port 21) ==========
def handle_ftp(conn, addr):

    log_path = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{addr[0]}_{addr[1]}.txt")
    with conn, open(log_path, "w") as log_file:

        try:
            print(f"[*] Connected by {addr} on port 21")
            log_file.write(f"{datetime.now()}: [*] Connected by {addr} on port 21\n")

            conn.sendall(b"220 (vsFTPd 3.0.5)\r\n")

            attempts = 0
            while attempts < 4:
                data = recv_line(conn)

                if not data:
                    print(f"[*] No data received from {addr}. Closing connection.")
                    log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                    parent_log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                    conn.close()
                    return

                command = data.decode(errors='ignore').strip()
                print(f"[*] Received data from {addr}: {command}")
                log_file.write(f"{datetime.now()}: [*] Received data from {addr}: {command}\n")

                if command.lower().startswith("user"):
                    conn.sendall(b"331 Please specify the password.\r\n")
                    password = recv_line(conn)

                    if not password:
                        print(f"[*] No password recieved from {addr}. Closing connection.")
                        log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                        parent_log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                        conn.close()
                        return

                    log_file.write(f"{datetime.now()}: [*] Received password from {addr}: {password.decode(errors='ignore')}\n")
                    print(f"[*] Received password from {addr}: {password.decode(errors='ignore')}\n")
                    conn.sendall(b"530 Login incorrect.\r\n")
                    attempts = attempts + 1
                else:
                    conn.sendall(b"530 Please login with USER and PASS.\r\n")

            # After exiting the loop
            conn.sendall(b"421 Service not available, remote server has closed connection\r\n")
            log_file.write(f"{datetime.now()}: [*] {addr} has exceeded the maximum number of attempts. Closing connection\n")
            parent_log_file.write(f"{datetime.now()}: [*] {addr} has exceeded the maximum number of attempts. Closing connection\n")
            conn.close()

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


#======== Telnet Client Handler (port 23) ==========
def handle_telnet(conn, addr):

    log_path = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{addr[0]}_{addr[1]}.txt")
    with conn, open(log_path, "w") as log_file:

        try:
            print(f"[*] Connected by {addr} on port 23")
            log_file.write(f"{datetime.now()}: [*] Connected by {addr} on port 23\n")

            conn.sendall(b"\r\nUbuntu 22.04.3 LTS\r\n")
            sleep(0.5)

            attempts = 0
            while attempts < 3:
                conn.sendall(b"login: ")
                username = recv_line(conn)

                if not username:
                    print(f"[*] No data received from {addr}. Closing connection.")
                    log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                    parent_log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                    conn.close()
                    return

                log_file.write(f"{datetime.now()}: [*] Received data from {addr}: {username.decode(errors='ignore').strip()}\n")
                print(f"[*] Received data from {addr}: {username.decode(errors='ignore').strip()}")

                conn.sendall(b"\nPassword: ")
                conn.sendall(IAC + WILL + ECHO)
                password = recv_line(conn)
                conn.sendall(IAC + WONT + ECHO)

                if not password:
                    print(f"[*] No password recieved from {addr}. Closing connection.")
                    log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                    parent_log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                    conn.close()
                    return

                log_file.write(f"{datetime.now()}: [*] Received password from {addr}: {password.decode(errors='ignore')}\n")
                print(f"[*] Received password from {addr}: {password.decode(errors='ignore')}\n")
                sleep(1)
                conn.sendall(b"\r\nLogin incorrect\r\n\r\n")
                attempts = attempts + 1

            # After exiting the loop
            conn.sendall(b"\r\nAttempts exceeded. You have been logged !!\r\n\r\n")
            log_file.write(f"{datetime.now()}: [*] {addr} has exceeded the maximum number of attempts. Closing connection\n")
            parent_log_file.write(f"{datetime.now()}: [*] {addr} has exceeded the maximum number of attempts. Closing connection\n")
            conn.close()

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


#======== SMTP Client Handler (port 587) ==========
def handle_smtp(conn, addr):

    log_path = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{addr[0]}_{addr[1]}.txt")
    with conn, open(log_path, "w") as log_file:

        try:
            print(f"[*] Connected by {addr} on port 587")
            log_file.write(f"{datetime.now()}: [*] Connected by {addr} on port 587\n")

            conn.sendall(b"220 mail.exchange.com ESMTP Postfix (Debian/GNU)\r\n")

            attempts = 0
            while attempts < 3:
                data = recv_line(conn)

                if not data:
                    print(f"[*] No data received from {addr}. Closing connection.")
                    log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                    parent_log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                    conn.close()
                    return

                command = data.decode(errors='ignore').strip()
                print(f"[*] Received data from {addr}: {command}")
                log_file.write(f"{datetime.now()}: [*] Received data from {addr}: {command}\n")

                if command.lower().startswith("ehlo") or command.lower().startswith("helo"):
                    conn.sendall(b"250-mail.example.com Hello\r\n250-PIPELINING\r\n250-SIZE 10240000\r\n250-STARTTLS\r\n250-AUTH LOGIN PLAIN\r\n250 8BITMIME\r\n")

                elif command.lower().startswith("auth login"):
                    conn.sendall(b"334 VXNlcm5hbWU6 Username:\r\n")
                    username = recv_line(conn)

                    if not username:
                        print(f"[*] No data received from {addr}. Closing connection.")
                        log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                        parent_log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                        conn.close()
                        return

                    log_file.write(f"{datetime.now()}: [*] Received username from {addr}: {username.decode(errors='ignore').strip()}\n")

                    conn.sendall(b"334 UGFzc3dvcmQ6 Password:\r\n")
                    password = recv_line(conn)

                    if not password:
                        print(f"[*] No password recieved from {addr}. Closing connection.")
                        log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                        parent_log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                        conn.close()
                        return

                    log_file.write(f"{datetime.now()}: [*] Received password from {addr}: {password.decode(errors='ignore').strip()}\n")
                    print(f"[*] Received password from {addr}: {password.decode(errors='ignore').strip()}\n")
                    conn.sendall(b"535 5.7.8 Authentication credentials invalid\r\n")
                    attempts = attempts + 1

                else:
                    conn.sendall(b"500 5.5.1 Command unrecognized\r\n")

            # After exiting the loop
            conn.sendall(b"421 4.7.0 Too many errors, closing connection.\r\n")
            log_file.write(f"{datetime.now()}: [*] {addr} has exceeded the maximum number of attempts. Closing connection\n")
            parent_log_file.write(f"{datetime.now()}: [*] {addr} has exceeded the maximum number of attempts. Closing connection\n")
            conn.close()

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


#======== HTTP Client Handler (port 80) ==========
def handle_http(conn, addr):

    log_path = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{addr[0]}_{addr[1]}.txt")
    with conn, open(log_path, "w") as log_file:

        try:
            print(f"[*] Connected by {addr} on port 80")
            log_file.write(f"{datetime.now()}: [*] Connected by {addr} on port 80\n")

            body = b"<html><body><h1>401 Unauthorized</h1><form method='POST' action='/login'>Username: <input name='u'><br>Password: <input name='p' type='password'><br><input type='submit'></form></body></html>"
            response = b"HTTP/1.1 200 OK\r\nServer: Apache/2.4.58 (Debian)\r\nContent-Type: text/html\r\nContent-Length: " + str(len(body)).encode() + b"\r\nConnection: keep-alive\r\n\r\n" + body

            attempts = 0
            while attempts < 3:
                data = recv_line(conn)

                if not data:
                    print(f"[*] No data received from {addr}. Closing connection.")
                    log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                    parent_log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                    conn.close()
                    return

                request_line = data.decode(errors='ignore').strip()
                print(f"[*] Received data from {addr}: {request_line}")
                log_file.write(f"{datetime.now()}: [*] Received data from {addr}: {request_line}\n")

                conn.sendall(response)
                attempts = attempts + 1

            # After exiting the loop
            log_file.write(f"{datetime.now()}: [*] {addr} has exceeded the maximum number of attempts. Closing connection\n")
            parent_log_file.write(f"{datetime.now()}: [*] {addr} has exceeded the maximum number of attempts. Closing connection\n")
            conn.close()

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


#======== HTTPS Client Handler (port 443) ==========
# No certificate is configured, so a real TLS handshake can't be completed here.
# just peek at the raw ClientHello bytes for logging/fingerprinting.
def handle_https(conn, addr):

    log_path = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{addr[0]}_{addr[1]}.txt")
    with conn, open(log_path, "w") as log_file:

        try:
            print(f"[*] Connected by {addr} on port 443")
            log_file.write(f"{datetime.now()}: [*] Connected by {addr} on port 443\n")

            data = conn.recv(4096)

            if not data:
                print(f"[*] No data received from {addr}. Closing connection.")
                log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                parent_log_file.write(f"{datetime.now()}: [*] {addr} has closed the connection voluntarily.\n")
                conn.close()
                return

            print(f"[*] Received TLS ClientHello ({len(data)} bytes) from {addr}")
            log_file.write(f"{datetime.now()}: [*] Received TLS ClientHello ({len(data)} bytes) from {addr}\n")
            conn.close()

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
            print(f"[*] Connected by {addr} on port 21")
            log_file.write(f"{datetime.now()}: [*] Connected by {addr} on port 21\n")

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
                print(f"[*] Received password from {addr}: {password.decode(errors='ignore')}\n")
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
            

"""

def serve(port): 

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
"""

sel = selectors.DefaultSelector()

ports = [21, 22, 23, 587, 443, 80]

for port in ports:
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind((HOST, port))
    lsock.listen()
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=port)

print(f"[*] Listening on {HOST}: {ports}")   # or build a PORTS list variable and reuse it here
          

parent_log_path = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_parent_log.txt")

with open(parent_log_path, "w") as parent_log_file:

    parent_log_file.write(f"{datetime.now()}: [*] Listening on {HOST}: {[21, 22]}\n")

        
    try:
        while True:
            events = sel.select(timeout = None)

            
            for key, _ in events:
                lsock = key.fileobj
                port = key.data
                conn, addr = lsock.accept()
                conn.setblocking(True)
                print(f"[*] Accepted connection from {addr} on port {port}")
                parent_log_file.write(f"{datetime.now()}: [*] Accepted connection from {addr} on port {port}\n")

                match port:
                    case 22:
                        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
                    case 21:
                        threading.Thread(target=handle_ftp, args=(conn, addr), daemon=True).start()
                    case 23:
                        threading.Thread(target=handle_telnet, args=(conn, addr), daemon=True).start()
                    case 587:
                        threading.Thread(target=handle_smtp, args=(conn, addr), daemon=True).start()
                    case 80:
                        threading.Thread(target=handle_http, args=(conn, addr), daemon=True).start()
                    case 443:
                        threading.Thread(target=handle_https, args=(conn, addr), daemon=True).start()

                        


    except KeyboardInterrupt:

        print("\n[!] Server shutting down. Starting Analysis.../")
        sleep(1.5)
        subprocess.run([sys.executable, "analyze-logs.py"])
        sys.exit(0)

    finally:
        sel.close()
