import serial
import time
# import argparse

ser = serial.Serial('COM5', 115200)
latencies = []
try:
    while True:
        recv = ser.readline().decode('utf-8').strip()
        if recv:
            print(recv)
            if "Sending..." in recv:
                print(time.time())
                start = time.time()
            if "And hello back to you" in recv:
                print(time.time())
                end = time.time()
                latencies.append(end-start)
                print("Latency: ", end-start)
except KeyboardInterrupt:
    print("Average latency: ", sum(latencies)/len(latencies))
    ser.close()
    exit(0)