import digitalio
import board
import busio
from adafruit_rfm9x import *
from adafruit_rfm9x import _RH_RF95_REG_0D_FIFO_ADDR_PTR, _RH_RF95_REG_00_FIFO, _RH_RF95_REG_22_PAYLOAD_LENGTH, _RH_RF95_REG_12_IRQ_FLAGS, _RH_RF95_REG_10_FIFO_RX_CURRENT_ADDR, _RH_RF95_REG_13_RX_NB_BYTES, _RH_RF95_REG_26_MODEM_CONFIG3

import logging
logger = logging.getLogger(__name__)

#Inherit Adafruit RFM9x Class to make RFM95 with custom packet headers
class RFM95(RFM9x):
    #Note: Overload send/recieve OR packetheader (dest, node, selfid, flags)
    def __init__(self,
        spi: SPI,
        cs: DigitalInOut,  # pylint: disable=invalid-name
        reset: DigitalInOut,
        frequency: int,
        *,
        preamble_length: int = 8,
        high_power: bool = True,
        baudrate: int = 5000000,
        agc: bool = False,
        crc: bool = True):
        super().__init__(
            spi, cs, reset, frequency,
            preamble_length=preamble_length,
            high_power=high_power,
            baudrate=baudrate,
            agc=agc,
            crc=crc)
        # Enable low data rate optimization
        self._write_u8(_RH_RF95_REG_26_MODEM_CONFIG3, 0x08) 
        # Defaulting to SF:12, 23dBm
        self.spreading_factor = 12
        self.tx_power=23
        # 4 Byte Packet Headers
        self._seq = 0
        self._ack = 0
        self._CMD = 0
        self._len = 0
    
    # Setters
    def setHeaders(self, seq:int, ack:int, CMD:int, length:int):
        self._seq = seq
        self._ack = ack
        self._CMD = CMD
        self._len = length
    
    def setSeq(self, seq:int):
        self._seq = seq
        
    def setAck(self, ack:int):
        self._ack = ack
        
    def setCMD(self, CMD:int):
        self._CMD = CMD
        
    def setLen(self, length:int):
        self._len = length
    
    # Getters
    def getSeq(self) -> int:
        return self._seq
    
    def getAck(self) -> int:
        return self._ack
    
    def getCMD(self) -> int:
        return self._CMD
    
    def getLen(self) -> int:
        return self._len
    
    def getHeaders(self) -> tuple:
        return (self._seq, self._ack, self._CMD, self._len)
    
    def extractHeaders(self, packet:bytearray) -> tuple:
        """Extract the headers from the packet and return them as a tuple."""
        seq     = packet[0]
        ack     = packet[1]
        CMD     = packet[2]
        length  = packet[3]
        data    = packet[4:]
        return (seq, ack, CMD, length, data)
    
    def send(
        self,
        data: ReadableBuffer,
        *,
        keep_listening: bool = False,
        seq: Optional[int] = None,
        ack: Optional[int] = None,
        CMD: Optional[int] = None,
        length: Optional[int] = None
    ) -> bool:
        """Send a string of data using the transmitter.
        You can only send 252 bytes at a time
        (limited by chip's FIFO size and appended headers).
        This appends a 4 byte header to be compatible with the RadioHead library.
        The header defaults to using the initialized attributes:
        (destination,node,identifier,flags)
        It may be temporarily overidden via the kwargs - destination,node,identifier,flags.
        Values passed via kwargs do not alter the attribute settings.
        The keep_listening argument should be set to True if you want to start listening
        automatically after the packet is sent. The default setting is False.

        Returns: True if success or False if the send timed out.
        """
        # Disable pylint warning to not use length as a check for zero.
        # This is a puzzling warning as the below code is clearly the most
        # efficient and proper way to ensure a precondition that the provided
        # buffer be within an expected range of bounds. Disable this check.
        # pylint: disable=len-as-condition
        assert 0 < len(data) <= 252
        # pylint: enable=len-as-condition
        self.idle()  # Stop receiving to clear FIFO and keep it clear.
        # Fill the FIFO with a packet to send.
        self._write_u8(_RH_RF95_REG_0D_FIFO_ADDR_PTR, 0x00)  # FIFO starts at 0.
        # Combine header and data to form payload
        payload = bytearray(4)
        if seq is None:  # use attribute
            payload[0] = self._seq
        else:  # use kwarg
            payload[0] = seq
        if ack is None:  # use attribute
            payload[1] = self._ack
        else:  # use kwarg
            payload[1] = ack
        if CMD is None:  # use attribute
            payload[2] = self._CMD
        else:  # use kwarg
            payload[2] = CMD
        if length is None:  # use attribute
            payload[3] = self._len
        else:  # use kwarg
            payload[3] = length
        payload = payload + data
        # Write payload.
        self._write_from(_RH_RF95_REG_00_FIFO, payload)
        # Write payload and header length.
        self._write_u8(_RH_RF95_REG_22_PAYLOAD_LENGTH, len(payload))
        # Turn on transmit mode to send out the packet.
        self.transmit()
        # Wait for tx done interrupt with explicit polling (not ideal but
        # best that can be done right now without interrupts).
        timed_out = False
        if HAS_SUPERVISOR:
            start = supervisor.ticks_ms()
            while not timed_out and not self.tx_done():
                if ticks_diff(supervisor.ticks_ms(), start) >= self.xmit_timeout * 1000:
                    timed_out = True
        else:
            start = time.monotonic()
            while not timed_out and not self.tx_done():
                if time.monotonic() - start >= self.xmit_timeout:
                    timed_out = True
        # Listen again if necessary and return the result packet.
        if keep_listening:
            self.listen()
        else:
            # Enter idle mode to stop receiving other packets.
            self.idle()
        # Clear interrupt.
        self._write_u8(_RH_RF95_REG_12_IRQ_FLAGS, 0xFF)
        return not timed_out
    
    def receive(
        self,
        *,
        keep_listening: bool = True,
        with_header: bool = True,
        timeout: Optional[float] = None
    ) -> Optional[bytearray]:
        """Wait to receive a packet from the receiver. If a packet is found the payload bytes
        are returned, otherwise None is returned (which indicates the timeout elapsed with no
        reception).
        If keep_listening is True (the default) the chip will immediately enter listening mode
        after reception of a packet, otherwise it will fall back to idle mode and ignore any
        future reception.
        All packets must have a 4-byte header for compatibility with the
        RadioHead library.
        The header consists of 4 bytes (To,From,ID,Flags). The default setting will  strip
        the header before returning the packet to the caller.
        If with_header is True then the 4 byte header will be returned with the packet.
        The payload then begins at packet[4].
        If with_ack is True, send an ACK after receipt (Reliable Datagram mode)
        """
        timed_out = False
        if timeout is None:
            timeout = self.receive_timeout
        if timeout is not None:
            # Wait for the payload_ready signal.  This is not ideal and will
            # surely miss or overflow the FIFO when packets aren't read fast
            # enough, however it's the best that can be done from Python without
            # interrupt supports.
            # Make sure we are listening for packets.
            self.listen()
            timed_out = False
            if HAS_SUPERVISOR:
                start = supervisor.ticks_ms()
                while not timed_out and not self.rx_done():
                    if ticks_diff(supervisor.ticks_ms(), start) >= timeout * 1000:
                        timed_out = True
            else:
                start = time.monotonic()
                while not timed_out and not self.rx_done():
                    if time.monotonic() - start >= timeout:
                        timed_out = True
        # Payload ready is set, a packet is in the FIFO.
        packet = None
        # save last RSSI reading
        self.last_rssi = self.rssi

        # save the last SNR reading
        self.last_snr = self.snr

        # Enter idle mode to stop receiving other packets.
        self.idle()
        if not timed_out:
            if self.enable_crc and self.crc_error():
                self.crc_error_count += 1
            else:
                # Read the data from the FIFO.
                # Read the length of the FIFO.
                fifo_length = self._read_u8(_RH_RF95_REG_13_RX_NB_BYTES)
                # Handle if the received packet is too small to include the 4 byte
                # RadioHead header and at least one byte of data --reject this packet and ignore it.
                if fifo_length > 0:  # read and clear the FIFO if anything in it
                    current_addr = self._read_u8(_RH_RF95_REG_10_FIFO_RX_CURRENT_ADDR)
                    self._write_u8(_RH_RF95_REG_0D_FIFO_ADDR_PTR, current_addr)
                    packet = bytearray(fifo_length)
                    # Read the packet.
                    self._read_into(_RH_RF95_REG_00_FIFO, packet)
                # Clear interrupt.
                self._write_u8(_RH_RF95_REG_12_IRQ_FLAGS, 0xFF)
                if fifo_length < 5:
                    packet = None
                else:
                    if (
                        not with_header and packet is not None
                    ):  # skip the header if not wanted
                        packet = packet[4:]
        # Listen again if necessary and return the result packet.
        if keep_listening:
            self.listen()
        else:
            # Enter idle mode to stop receiving other packets.
            self.idle()
        # Clear interrupt.
        self._write_u8(_RH_RF95_REG_12_IRQ_FLAGS, 0xFF)
        return packet
    
class RFM95Wrapper():
    """Wrapper for the RFM95 class to make it easier to use.
    It comes pre-initialized. Only need to provide the digitalio pins and frequency.
    The construct method returns the RFM95 object. To be used by the user.
    EDIT THIS CLASS IF YOU ARE CHANGING PIN OR FREQUENCY DEFAULTS.
    """
    def __init__(self, 
                 SCK:DigitalInOut = board.SCK,
                 MOSI:DigitalInOut = board.MOSI, 
                 MISO:DigitalInOut = board.MISO,
                 CS:DigitalInOut = digitalio.DigitalInOut(board.D26),
                 RESET:DigitalInOut = digitalio.DigitalInOut(board.D19),
                 FREQ:float = 915.0):
        self.spi = busio.SPI(SCK, MOSI=MOSI, MISO=MISO)
        self.rfm = RFM95(self.spi, CS, RESET, FREQ)
        self.rfm.setHeaders(0,0,0,0)
        
    def construct(self) -> RFM95:
        """Returns constructed ready-to-use RFM95 instance"""
        return self.rfm