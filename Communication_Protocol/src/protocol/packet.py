from .message import Message

class Packet:
    """
    Constructs the packet with a payload to be sent via LoRa
    """
    CALLSIGN = b"EXMP"
    
    def __init__(self, message: Message, flags, seq=0, ack=0):
        self.packet = []
        
        self.msg = message.get_bytes()
        self.msg_cmd, self.msg_len, self.msg_data = self.msg
        
        self.flags = flags
        self.seq = seq
        self.ack = ack
        self.checksum=None
    
    
    def construct_packet(self):
        """
        Constructs the packet
        :param None
        :return: packet: List[bytes]
        """
        self.checksum=self._compute_checksum(self.msg, self.flags, self.seq, self.ack)
        
        # self.packet = [
        #     self.CALLSIGN,
        #     self.flags.to_bytes(2, byteorder='big'),
        #     self.seq.to_bytes(1, byteorder='big'),
        #     self.ack.to_bytes(1, byteorder='big'),
        #     self.msg_cmd,
        #     self.msg_len,
        #     self.checksum,
        #     self.msg_data
        # ]
        # return self.packet
        return self
    
    def increment_seq(self):
        """
        Increments the sequence number
        :return: reconstructed packet: bytes
        """
        self.seq += 1
        return self.construct_packet()
    
    def increment_ack(self):
        """
        Increments the acknowledgement number
        :return: reconstructed packet: bytes
        """
        self.ack += 1
        return self.construct_packet()
    
    def set_seq(self, seq):
        """
        Sets the sequence number
        :param seq: int
        :return: reconstructed packet: bytes
        """
        self.seq = seq
        return self.construct_packet()
    
    def set_ack(self, ack):
        """
        Sets the acknowledgement number
        :param ack: int
        :return: reconstructed packet: bytes
        """
        self.ack = ack
        return self.construct_packet()
    
    def set_flags(self, flags):
        """
        Sets the flags of the packet
        :param flags: bytes
        :return: reconstructed packet: bytes
        """
        self.flags = flags
        return self.construct_packet()
    
    def get_packet(self):
        """
        Gets the packet
        :return: packet: bytes
        """
        return self
    
    def _compute_checksum(self, msg, flags, seq, ack):
        """
        Computes the checksum of the packet
        :param msg: Tuple[bytes, bytes. bytes]
        :return: checksum: bytes
        """
        proto_packet = flags.to_bytes(2, byteorder='big') + seq.to_bytes(2, byteorder='big') + ack.to_bytes(1, byteorder='big') + msg[0] + msg[1] + b"\x00" + msg[2] #Checksum in protopacket set to 0 for now
        segments = [proto_packet[i:i+2] for i in range(0, len(proto_packet), 2)]
        checksum = 0
        for segment in segments:
            checksum += int.from_bytes(segment, byteorder='big')
        checksum += checksum >> 16
        checksum = ~checksum & 0xffff #0xffff is the 16 bit mask to ensure the ~ operator returns a 16 bit unsigned integer
        return checksum.to_bytes(2, byteorder='big')