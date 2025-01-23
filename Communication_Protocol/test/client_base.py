from protocol import Message, Packet

class Client:
    
    def __init__(self):
        self.packet = b""
        self.recv_packet = b""
        
    def construct_packet(self, command, data=None):
        """
        Constructs the packet
        :param message: Message object
        :return: None
        """
        message = Message(command, data)
        message.encode()
        packet = Packet(0, 0, 0, message)
        packet.construct_packet()
        pass