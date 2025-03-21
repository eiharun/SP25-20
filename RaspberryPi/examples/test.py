import digitalio
import board
import busio
import adafruit_rfm9x
import time

RADIO_FREQ_MHZ = 915.0
CS = digitalio.DigitalInOut(board.D26)
RESET = digitalio.DigitalInOut(board.D24)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ, high_power=True)
#rfm9x.reset()
rfm9x._write_u8(0x26, 0x08) # Enable low data rate optimization
rfm9x.tx_power=23
rfm9x.spreading_factor=12
IDLE_WAIT=True
while True:
    payload = input("Enter message to send: ")

    while IDLE_WAIT:
        idle = rfm9x.receive(timeout=20)
        print("Idle: ", idle)
        if b"IDLE" in idle:
            IDLE_WAIT=False

    rfm9x.send(bytes(payload, "utf-8"))
    if(rfm9x.tx_done):
        print("Sent packet: ", payload)
        packet = rfm9x.receive(timeout=10)

        if packet is None:
            print("Recieved Nothing")

        else:
            print(f"Recieved: {str(packet,'ascii')}")
            print(f"Signal Strength: {rfm9x.last_rssi}")
            #time.sleep(1);