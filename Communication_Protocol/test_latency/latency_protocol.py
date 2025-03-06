import serial
import time
from datetime import datetime
import argparse

# get the filename from the command line (REQUIRED)
parser = argparse.ArgumentParser(description='Test latency of the communication protocol')
parser.add_argument('filename', type=str, help='Name of the file to write the data to')
args = parser.parse_args()
filename = args.filename

#if the file exists, append a counter to the filename
counter = 0
while True:
    try:
        with open(filename, "x") as f:
            break
    except FileExistsError:
        counter += 1
        filename = args.filename + str(counter)

 

ser = serial.Serial('COM7', 115200)
latencies = []
try:
    with open(filename, "w") as f:
        while True:
            recv = ser.readline().decode('utf-8').strip()
            if recv:
                if "Type data" in recv:
                    send=input("Type Y to send: ")
                    if send == "Y":
                        ser.write(b"A\n")
                now = datetime.now()
                f.write(now.strftime("%Y-%m-%d %H:%M:%S.%f") + ", " + recv + "\n")
                print(recv)
                if "Sending..." in recv:
                    print(time.time())
                    start = time.time()
                if "Sending SYN/ACK..." in recv:
                    print(time.time())
                    end = time.time()
                    latencies.append(end-start)
                    print("Latency: ", end-start)
                    f.write("Latency: " + str(end-start) + "\n")
except KeyboardInterrupt:
    if(len(latencies) == 0):
        print("No packets sent")
        exit(0)
    print("Average latency: ", sum(latencies)/len(latencies))
    with open(filename, "a") as f:
        f.write("Average latency: " + str(sum(latencies)/len(latencies)) + "\n")
    ser.close()
    exit(0)