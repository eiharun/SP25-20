from rfm95api import *

constructor = RFM95Wrapper()
rfm95 = constructor.construct()
payload = b"Hello World"

rfm95.send(payload, 1,0,64,len(payload))
# Below has the same effect as above
# rfm95.setHeaders(1,0,64,len(payload))
# rfm95.send(payload)
rfm95.send(bytes(payload, "utf-8"))
if(rfm95.tx_done):
    print("Sent packet: ", payload)
    packet = rfm95.receive(timeout=10)

    if packet is None:
        print("Recieved Nothing")

    else:
        print(f"Recieved: {str(packet,'ascii')}")
        print(f"\tSignal Strength: {rfm95.last_rssi}")
        print(f"\tSNR: {rfm95.last_snr}")
        time.sleep(0.1)