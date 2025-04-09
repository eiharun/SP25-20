import serial
import time
from datetime import datetime
import argparse
import os

parser = argparse.ArgumentParser(prog="seriallog.py", description='Test latency of the communication protocol', usage="%(prog)s COM7 log.txt")
parser.add_argument('port', type=str, help='COM port the device is connected to')
parser.add_argument('filename', type=str, help='[DESCRIPTIVE] Name of the log file')
args = parser.parse_args()
filename = args.filename
port = args.port

logdir = "./logs/"
# Create the logs directory if it doesn't exist
if not os.path.exists(logdir):
    print("Creating logs directory")
    os.makedirs(logdir)

if filename.rfind('.') == -1:
    # add .txt extension if it doesn't exist
    print("No file extension found, adding .txt")
    filename += ".txt"

filedir = os.path.join(logdir, filename)
    
counter = 0
filename_count=filename
while True:
    try:
        with open(filedir, "x") as f:
            break
    except FileExistsError:
        print("File already exists, adding counter to filename")
        counter += 1
        # move file extentio after the counter
        filename_count = filename[:filename.rfind('.')] + str(counter) + filename[filename.rfind('.'):]
        filedir = os.path.join(logdir, filename_count)
        
try:
    ser = serial.Serial(port, 115200)
except serial.SerialException as e:
    print("Error opening serial port: ", e)
    print("Make sure you entered the correct port and the device is connected")
    os.remove(filedir)
    exit(1)
latencies = []
try:
    start = None
    while True:
        with open(filedir, "a") as f:
            recv = ser.readline().decode('utf-8').strip()
            if recv:
                now = datetime.now()
                f.write(now.strftime("%Y-%m-%d %H:%M:%S.%f") + ", " + recv + "\n")
                print(recv)
                if "Sending..." in recv:
                    start = time.monotonic()
                if "Got reply" in recv:
                    if not start:
                        continue
                    end = time.monotonic()
                    latencies.append(end-start)
                    print("PyLatency: ", end-start)
                    f.write("PyLatency: " + str(end-start) + "\n")
except KeyboardInterrupt:
    if(len(latencies) == 0):
        print("No packets sent")
        exit(0)
    print("Average latency: ", sum(latencies)/len(latencies))
    with open(filedir, "a") as f:
        f.write("Average latency: " + str(sum(latencies)/len(latencies)) + "\n")
    ser.close()
    exit(0)