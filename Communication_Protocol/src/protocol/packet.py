from .message import Message

class Packet:
    """
    Constructs the packet with a payload to be sent via LoRa
    """
    CALLSIGN = b"EXMP"
    
    def __init__(self, seq, ack, rep, message: Message):
        self.packet = b""
        
        if message.payload is None:
            message.encode()#Encode the message if not already encoded
        self.payload: bytes = message.get_payload()
        
        self.seq = seq
        self.ack = ack
        self.rep = rep
        
    
    def construct_packet(self):
        """
        Constructs the packet
        :param message: None
        :return: packet: bytes
        """
        self.packet = self.CALLSIGN 
        self.packet += self.seq.to_bytes(2, byteorder='big') + self.ack.to_bytes(2, byteorder='big') + self.rep.to_bytes(2, byteorder='big')
        checksum = self._compute_checksum(self.packet)
        self.packet += checksum
        self.packet += self.payload
        return self.packet
        
    def increment_seq(self):
        """
        Increments the sequence number
        """
        pass
    
    def increment_ack(self):
        """
        Increments the acknowledgement number
        """
        pass
    
    def increment_rep(self):
        """
        Increments the repetition number
        """
        pass
    
    def _compute_checksum(self, header: bytes):
        """
        Computes the checksum of the packet header
        :param header: bytes
        :return: checksum: bytes
        """
        segments = [header[i:i+2] for i in range(0, len(header), 2)]
        checksum = 0
        for segment in segments:
            checksum += int.from_bytes(segment, byteorder='big')
        checksum += checksum >> 16
        checksum = ~checksum & 0xffff #0xffff is the 16 bit mask to ensure the ~ operator returns a 16 bit unsigned integer
        return checksum.to_bytes(2, byteorder='big')