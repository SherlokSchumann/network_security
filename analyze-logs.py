# Get the file names of all files with "parent_log"
# Extract all data from these files and write them to a new file called combined_parent_log.txt in an /analysis dir
# For all unique IP addresses, extract the start and end time of all their connections to a list using tuples
# using numpy create a table.
# add another column to the table that calculated the duration of each connection in seconds.

# create another table with IP, number of attempts, time between each attempt

import re
import os
import numpy as np
import pandas as pd
import dataframe_image as dfi
from datetime import datetime
import math
from collections import Counter


LOG_DIR = "logs"

HOST_LOG_PATTERN = re.compile(r"^log_.*\.txt$")

FILENAME_PATTERN = re.compile(
    r"^log_(?P<date>\d{4}-\d{2}-\d{2})_(?P<time>\d{2}-\d{2}-\d{2})_"
    r"(?P<ip>\d{1,3}(?:\.\d{1,3}){3})_(?P<port>\d+)\.txt$"
)



CLOSED_LINE_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+): \[\*\] "
    r"Connection with \('(?P<ip>\d{1,3}(?:\.\d{1,3}){3})', (?P<port>\d+)\) closed\.$"
)

OPEN_LINE_PATTERN = CONNECTED_LINE_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+): \[\*\] "
    r"Connected by \('(?P<ip>\d{1,3}(?:\.\d{1,3}){3})', (?P<port>\d+)\)$"
)


IPs = {}

files = [f for f in os.listdir(LOG_DIR) if HOST_LOG_PATTERN.match(f)]

for file in files:
    match = FILENAME_PATTERN.match(file)
    date, time, ip, port = None, None, None, None
    if match:
        date = match.group("date")
        time = match.group("time")
        ip = match.group("ip")
        port = match.group("port")
        print(f"File: {file}, Date: {date}, Time: {time}, IP: {ip}, Port: {port}")
    if ip in IPs.keys():
        count = IPs[ip]["count"]
        IPs[ip]["count"] = count + 1
        IPs[ip]["date"].append(date)
        IPs[ip]["time"].append(time)
    else:
        IPs[ip] = {"count": 1, "date": [date], "time": [time], "port": port}
    

# print(f"IPs: {IPs}")

dict = {} # {IP: [(starting, closing), (starting, closing)], IP:....}

for file in files:
    with open(os.path.join(LOG_DIR, file), "r") as log_file:
        ip, timestamp_start, timestamp_end = None, None, None
        for line in log_file:
            match = OPEN_LINE_PATTERN.match(line)
            
            if match:
                ip = match.group("ip")
                timestamp_start = match.group("timestamp")

            match = CLOSED_LINE_PATTERN.match(line)
            if match:
                timestamp_end = match.group("timestamp")

        if ip in dict.keys():
            dict[ip].append((timestamp_start, timestamp_end))
        else:
            dict[ip] = [(timestamp_start, timestamp_end)]
    
# print(f"dict: {dict}")
            
            
# Create multiple dataFrames and display them

# counts dictionsry
counts = {}
ip_list = [ip for ip in IPs]
for IP in IPs:
    counts[IP] = IPs[IP]["count"]

df_counts = pd.DataFrame(list(counts.items()), columns=["ip", "count"])
pd.set_option("display.max_rows", None)     # show all rows
pd.set_option("display.max_columns", None)  # show all columns
pd.set_option("display.width", None) 


print(f"\n\n")
print(f"------------------------------ HONEYPOT ANALYSIS -------------------------------------\n\n")
print(f"=========== SUMMARY OF ATTACK RESULTS ============\n")
print(df_counts)
print(f"\n")

dict_list = []

key = ("date", "login_time", "start_time", "end_time", "elapsed_time_after_prev_login")
for ip in ip_list:
    for i in range(counts[ip]):
      

        fmt = "%H:%M:%S.%f"
        diff = 0
        if(i != 0):
            start_time_now = dict[ip][i][0].split(" ")[1]
            start_time_prev = dict[ip][i - 1][0].split(" ")[1]

            dt2 = datetime.strptime(start_time_now, fmt)
            dt1 = datetime.strptime(start_time_prev, fmt)
            diff = abs((dt2 - dt1).total_seconds())

        info = {ip: [(IPs[ip]["date"][i], IPs[ip]["time"][i].replace("-", ":"), dict[ip][i][0].split(" ")[1], dict[ip][i][1].split(" ")[1], diff)]}
        dict_list.append(info)


columns = ["date", "login_time", "start_time", "end_time", "elapsed_time_after_prev_login"]

# flatten: {ip: [(...)]} entries -> rows with ip attached
rows = []
for entry in dict_list:
    for ip, records in entry.items():
        for record in records:
            rows.append((ip, *record))

df = pd.DataFrame(rows, columns=["ip", *columns])

# print one table per IP
for ip, group in df.groupby("ip"):
    print(f"\n=== {ip} ===\n")
    print(group.drop(columns="ip").to_string(index=False))



print(f"\n\n============= Flags / Warning behaviours ===========\n")

# Time window: 40 seconds

sec = 80
look_time = 0
freq_list = []
for entry in dict_list:
    ip = list(entry.keys())[0]
    if entry[ip][0][4] <= sec:
        freq_list.append(ip)
    else:
        break


top_two = Counter(freq_list).most_common(1)
print(f"\nThe hosts to be flagged are: \n")
for item in top_two:
    print(f"IP address: {item[0]}, Number of attempts: {item[1]} in {sec} seconds ")

print(f"\n\n")
print(f"\n-------------------------------- End Of Analysis ------------------------------------\n")








    
