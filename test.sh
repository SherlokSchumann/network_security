#!/bin/bash
# ==============================================================================
# CAPE Sandbox Verification Script
# Purpose: Simulates Privilege Escalation & Network Connections (Benign)
# Reference: Inspired by MITRE ATT&CK T1068 & T1001
# ==============================================================================

echo "[*] Starting CAPE Sandbox Test Script..."

# ------------------------------------------------------------------------------
# SECTION 1: Privilege Escalation & Discovery Simulation
# ------------------------------------------------------------------------------
echo "[*] Simulating Privilege Escalation / Auditing Behavior..."

# 1. Check current user and groups
whoami
groups

# 2. Check sudo privileges (often monitored by sandbox rules)
sudo -n -l 2>/dev/null

# 3. Search for files with SUID permission bits (common priv-esc target)
echo "[*] Searching for SUID binaries (limited to /bin for speed)..."
find /bin -perm -4000 -type f 2>/dev/null | head -n 5

# 4. Attempt to access a sensitive file (triggers a benign "Permission Denied")
echo "[*] Attempting to read protected file..."
cat /etc/shadow 2>/dev/null

# ------------------------------------------------------------------------------
# SECTION 2: Network Connection & Command and Control (C2) Simulation
# ------------------------------------------------------------------------------
echo "[*] Simulating Network Connections / Steganography Behavior..."

# 1. Standard DNS lookup and HTTP request to a safe domain
echo "[*] Testing standard outbound network connection..."
curl -s -o /dev/null -w "%{http_code}" https://google.com

# 2. Network connection using alternative binaries (Living off the Land)
echo "[*] Testing alternative network connection via wget..."
wget --spider -q https://wikipedia.org

# 3. Simulating MITRE ATT&CK T1001.002 (Steganography / Appended Data)
# This appends data to a benign text file to mimic covert signaling
echo "[*] Simulating T1001.002 data appending..."
echo "BENIGN_C2_DATA_MARKER" >> /tmp/cape_test_signal.txt

echo "[*] Script execution finished."

