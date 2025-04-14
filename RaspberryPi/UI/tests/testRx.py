from rfm95api import *

rfm95 = RFM95Wrapper().construct()
#rfm9x.reset()
seq_num = 0
while True:
        packet = rfm95.receive(timeout=10)
        if packet is None:
            print("Recieved Nothing")
        else:
            seq, ack, cmd, length, data = rfm95.extractHeaders(packet)
            recv = str(packet, 'ascii')
            print(f"Recieved: {str(packet,'ascii')}")
            print(f"\tSignal Strength: {rfm95.last_rssi}")
            print(f"\tSNR: {rfm95.last_snr}")
            rfm95.send(f"Acked: {recv[9:]}".encode('utf-8'), seq=seq_num, ack=seq+1,CMD=cmd, length=0)
            seq_num = (seq_num + 1) % 256
            print("\tSend Ack")
            time.sleep(0.1)
