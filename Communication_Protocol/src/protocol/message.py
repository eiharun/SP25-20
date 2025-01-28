from .commands import Commands

NO_DATA = 64
BCD_DATA = 194
TBD_DATA = 256   

class Message:
    """
    Constructs a dataclass object that stores the command, data, and length of the data.
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
            self.data = data if data else None
            self.length = len(data) if data else 0
        else:
            raise ValueError("Invalid command: Out of Range")
        
        if self.length > 2^self.LENGTH_BIT_LEN:
            raise ValueError("Data length exceeds maximum bit length of {}".format(self.LENGTH_BIT_LEN))
        
    def get_bytes(self):
        command_bytes = self.command.value.to_bytes(1, byteorder='big')
        length_bytes = self.length.to_bytes(1, byteorder='big')
        if self.data:
            if isinstance(self.data, str):
                data_bytes = self._pad(self.data.encode("utf-8"))
            else:
                data_bytes = self._pad(self.data.to_bytes(self.length, byteorder='big'))
        else:
            data_bytes = b""
        
        return command_bytes, length_bytes, data_bytes
    
    def _pad(self, data: bytes):
        """
        Pads the data to a 4 byte boundary PKCS#7 
        """
        return data + bytes([4-len(data)%4]*(4-len(data)%4))
        