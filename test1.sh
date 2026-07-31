{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 #!/bin/bash\
\
# 1. Network Activity Indicator\
# Contacts a harmless URL to trigger DNS and HTTP/HTTPS network logs\
echo "[*] Contacting www.cricinfo.com..."\
curl -s -I https://cricinfo.com > /dev/null\
\
# 2. Process Creation Indicator\
# Starts the nano text editor in the background, waits 2 seconds, then terminates it\
echo "[*] Launching nano editor..."\
nano &\
NANO_PID=$!\
sleep 2\
kill $NANO_PID 2>/dev/null\
\
# 3. Privilege Escalation Indicator\
# Attempts a non-interactive sudo command to trigger authentication/privilege logs\
echo "[*] Attempting sudo command..."\
sudo -n true 2>/dev/null\
\
echo "[*] Test script execution completed."\
}