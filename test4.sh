{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 #!/bin/bash\
# ==============================================================================\
# CAPE Sandbox Behavior Verification Script\
# Purpose: Simulates Defense Evasion & Persistence Actions (Benign)\
# Reference: Inspired by MITRE ATT&CK T1562 (Evasion) & T1547 (Persistence)\
# ==============================================================================\
\
echo "[*] Starting CAPE Sandbox Evasion & Persistence Test Script..."\
\
# ------------------------------------------------------------------------------\
# SECTION 1: Defense Evasion & Security Subversion Simulation\
# ------------------------------------------------------------------------------\
echo "[*] Simulating Defense Evasion / Environment Auditing..."\
\
# 1. Check for common sandbox artifacts or environment variables\
echo "[*] Checking system uptime to detect low-uptime environments..."\
uptime\
\
# 2. Check for active security logging services (common defense auditing)\
echo "[*] Checking status of system logging services..."\
systemctl status rsyslog 2>/dev/null | grep "Active:" || echo "[!] systemctl not available"\
\
# 3. Check for specific debugging or tracing mechanisms\
echo "[*] Checking if current process is running under a debugger..."\
grep -i "TracerPid" /proc/self/status 2>/dev/null\
\
# 4. Attempt to modify or read a local firewall rule configuration\
echo "[*] Simulating firewall state discovery..."\
iptables -L -n 2>/dev/null || echo "[!] Insufficient permissions to read iptables (Expected)"\
\
# ------------------------------------------------------------------------------\
# SECTION 2: Persistence Mechanism Simulation\
# ------------------------------------------------------------------------------\
echo "[*] Simulating Persistence / Scheduled Execution Behavior..."\
\
# 1. Attempt to enumerate cron jobs for the current user\
echo "[*] Enumerating active scheduled tasks (Crontab)..."\
crontab -l 2>/dev/null\
\
# 2. Simulate persistence by creating a benign file in a temporary startup-like directory\
echo "[*] Writing a mock persistence marker to /tmp..."\
echo "#!/bin/sh" > /tmp/cape_persistence_mock.sh\
echo "echo 'Benign Persistence Test'" >> /tmp/cape_persistence_mock.sh\
chmod +x /tmp/cape_persistence_mock.sh\
\
# 3. Enumerate system-wide shell profiles (often targeted for broad user-level persistence)\
echo "[*] Auditing global profile scripts..."\
ls -la /etc/profile.d/ 2>/dev/null | head -n 5\
\
echo "[*] Script execution finished."\
}