SSH HONEYPOT
============

Note: Support for multiple ports has been added !

A lightweight SSH honeypot written in Python for a Network Security
project. It listens on a TCP port, impersonates an OpenSSH server, and logs
everything an attacker does — including the passwords they try — without
ever granting real access. A companion script parses the resulting logs
into readable per-attacker session tables and flags suspicious rapid-fire
login attempts.

WHAT IT DOES
------------
honeypot.py:
  - Opens a TCP socket (default 0.0.0.0:22) and accepts connections using
    a thread per client.
  - Peeks at the first byte of traffic to distinguish Telnet clients from
    raw TCP/SSH clients (detectClient).
  - Sends a fake OpenSSH 10.0 version banner and a spoofed ED25519 host
    key fingerprint prompt, mimicking a real first-time SSH connection.
  - Waits for a yes/no host-key confirmation, then simulates a password
    prompt loop, accepting up to 6 password attempts before kicking the
    client with "maximum number of attempts exceeded".
  - Logs every event (connect, host-key response, each password attempt,
    disconnects, errors) with timestamps to a logs/ folder (created
    automatically if it doesn't exist):
      * a per-connection log file: logs/log_<date>_<time>_<ip>_<port>.txt
      * a shared per-run parent log: logs/<date>_<time>_parent_log.txt
  - On Ctrl+C, gracefully shuts down and automatically kicks off
    analyze-logs.py to summarize the session.

analyze-logs.py:
  - Scans the logs/ folder for all log_*.txt session files.
  - Extracts connect/close timestamps and password attempts per IP.
  - Builds summary tables (via pandas/numpy) showing, per attacker IP:
    number of connection attempts, login/start/end times, and elapsed
    time since the previous attempt.
  - Flags hosts that reconnect unusually fast (within an 80-second
    window), which is a strong indicator of automated/scripted attacks
    rather than manual probing.

USAGE
-----
Requirements: Python 3, pandas, numpy, dataframe_image

1. Run the honeypot (requires root/sudo to bind to port 22, or change
   PORT in honeypot.py to an unprivileged port for testing):

     sudo python3 honeypot.py

2. Point an SSH/Telnet/netcat client at the host to generate traffic, e.g.:

     ssh debian@<honeypot-ip>
     nc <honeypot-ip> 22

3. Stop the honeypot with Ctrl+C. It will automatically run the log
   analysis and print a summary of all captured sessions and any flagged
   IPs to the console.

   Analysis can also be run manually at any time against existing logs:

     python3 analyze-logs.py

NOTES
-----
This is a research/educational tool intended for controlled, authorized
environments (e.g. a lab VM or isolated network) — not for deployment
against production infrastructure or without permission from the network
owner.

---

Open to collaboration — feel free to reach out with ideas, issues, or
pull requests.

my email: adithyav053@gmail.com

