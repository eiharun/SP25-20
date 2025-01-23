from .commands import Commands
from math import log2

NO_DATA = 64
BCD_DATA = 194
TBD_DATA = 256   

class Message:
    """
    Constructs a payload object that can be used as a payload data for a packet using TLV encoding.
    """
    TAG_BIT_LEN = 8 #bits
    LENGTH_BIT_LEN = 8 #bits
    
    def __init__(self, command, data=None):
        try:
            self.command = Commands[command.upper()]
        except KeyError:
            raise ValueError("Invalid command: Not Found")
        if self.command.value < NO_DATA: #No data
            self.data=None
            self.length=0
        elif self.command.value >= NO_DATA and self.command.value < BCD_DATA: #BCD data encoding
            if data is None:
                raise ValueError("Invalid data for BCD command: Missing")
            self.data = int(data)
            self.length = (self.data//255)+1 #num of bytes in data
        elif self.command.value >= BCD_DATA and self.command.value < TBD_DATA: #TBD data encoding
            #TBD: ascii encoding for now
            self.data = bytes(data, 'utf-8') if data else None
            self.length = len(data) if data else 0
        else:
            raise ValueError("Invalid command: Out of Range")
        if self.length > 2^self.LENGTH_BIT_LEN:
            raise ValueError("Data length exceeds maximum bit length of {}".format(self.LENGTH_BIT_LEN))
        
        self.payload=None
    
    def encode(self):
        """
        Encodes the payload data into bytes using TLV encoding.
            self.payload contains the TLV encoded data in integer form.
        :return: Encoded payload data in bytes
        """
        if self.command.value < NO_DATA: #No data
            self.payload = self.command.value << (self.LENGTH_BIT_LEN*self.length + self.TAG_BIT_LEN)
            self.payload |= self.length << self.length*8
            return self.payload.to_bytes(2, byteorder='big')
        
        elif self.command.value >= NO_DATA and self.command.value < BCD_DATA: #BCD data encoding
            self.payload = self.command.value << (self.LENGTH_BIT_LEN*self.length + self.TAG_BIT_LEN)
            self.payload |= self.length << self.length*8
            self.payload |= int(self.data)
            return self.payload.to_bytes(2+self.length, byteorder='big')
        
        elif self.command.value >= BCD_DATA and self.command.value < TBD_DATA: #TBD data encoding
            #TBD: ascii encoding for now
            self.payload = self.command.value << (self.LENGTH_BIT_LEN*self.length + self.TAG_BIT_LEN)
            self.payload |= self.length << self.length*8
            if self.data:
                for n, byte in enumerate(self.data):
                    self.payload |= byte << n*8
            return self.payload.to_bytes(2+self.length, byteorder='big')
        
        else:
            raise ValueError("Invalid command: Out of Range")
    
    # def construct(self):
    #     """
    #     Constructs the TLV encoded payload into a packet payload with FEC.
    #     """
        
    #     pass

    def decode(self, tlv):
        """
        Decodes the TLV encoded payload into a TAG/Command and Value.
        :param tlv: TLV encoded data in bytes OR integer form
        :return: Tuple[Tag,Length,Value] in bytes
        """
        pass

    def __str__(self):
        return self.payload.to_bytes(2+self.length, byteorder='big')
    
    def __repr__(self):
        #TODO: use decode()
        return self.payload.to_bytes(2+self.length, byteorder='big').hex()
    
    def get_payload(self):
        return self.payload.to_bytes(2+self.length, byteorder='big')