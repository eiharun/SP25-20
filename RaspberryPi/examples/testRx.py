import digitalio
import board
import busio
import adafruit_rfm9x
import time

RADIO_FREQ_MHZ = 915.0
CS = digitalio.DigitalInOut(board.D26)
RESET = digitalio.DigitalInOut(board.D19)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ, high_power=True)
#rfm9x.reset()
rfm9x.tx_power=23
rfm9x.spreading_factor=12
rfm9x.signal_bandwidth=125000
rfm9x._write_u8(0x26, 0x08) # Enable low data rate optimization
while True:
        packet = rfm9x.receive(timeout=10)
        if packet is None:
            print("Recieved Nothing")
        else:
            recv = str(packet, 'ascii')
            print(f"Recieved: {str(packet,'ascii')}")
            print(f"\tSignal Strength: {rfm9x.last_rssi}")
            print(f"\tSNR: {rfm9x.last_snr}")
            rfm9x.send(f"Acked: {recv[9:]}".encode('utf-8'))
            print("\tSend Ack")
            time.sleep(0.1)
