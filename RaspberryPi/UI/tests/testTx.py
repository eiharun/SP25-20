from rfm95api import *

constructor = RFM95Wrapper()
rfm95 = constructor.construct()
payload = b"Hello World"

rfm95.send(payload, seq=255, ack=0, CMD=64, length=len(payload))
# Below has the same effect as above
# rfm95.setHeaders(1,0,64,len(payload))
# rfm95.send(payload)
if(rfm95.tx_done):
    print("Sent packet: ", payload)
    packet = rfm95.receive(timeout=10)

    if packet is None:
        print("Recieved Nothing")

    else:
        print(f"Recieved: {packet}")
        print(f"\tSignal Strength: {rfm95.last_rssi}")
        print(f"\tSNR: {rfm95.last_snr}")
        time.sleep(0.1)
