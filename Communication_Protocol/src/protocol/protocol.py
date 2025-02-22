import asyncio
import random
from enum import Enum
from .packet import Packet
from .message import Message
from .commands import Flags

class States(Enum):
    CLOSED = 0
    AWAIT_S_A = 1 #Syn sent triggers this state, after timer expires, it will resend the syn packet
    S_A_RECEIVED = 2 #Syn/Ack received triggers this state, as a reaction it sends an ack packet and transitions to AWAIT_S
    S_RECEIVED = 3 #Syn received triggers this state, as a reaction it sends a syn/ack packet and transitions to AWAIT_A
    AWAIT_A = 4  #Syn/Ack sent triggers this state, after timer expires, it will resend the syn/ack packet
    EXECUTE = 5 #Executes command and transitions to CLOSED
    SEND_SYN = 6
    A_RECEIVED = 7

MAX_SEQ_NUM = 254
RETRY_LIMIT = 254
TIMEOUT = 5.0


class Protocol:
    def __init__(self):
        self.state = States.CLOSED
        self.seq_num = 0
        self.ack_num = 0
        self.timeout = False
        self.retries = 0
        self.recv_packet = None
        self.sent_packet = None
    
    def run(self, packet: Packet) -> Packet:
        match self.state:
            case States.CLOSED:
                if packet.flags == Flags.SYN_ACK.value: #Packet is Syn/Ack Packet
                    self.ack_num = packet.seq_num+1
                    self.seq_num = (self.seq_num + 1) % MAX_SEQ_NUM
                    self.state = States.S_A_RECEIVED
                    return Packet(Message("TEST"),Flags.ACK.value, self.seq_num, self.ack_num)
                elif packet.flags == Flags.SYN.value: #Packet is Syn packet
                    self.ack_num = packet.seq_num+1
                    self.seq_num = (self.seq_num + 1) % MAX_SEQ_NUM
                    self.state = States.S_RECEIVED
                    return Packet(Message("TEST"),Flags.SYN_ACK.value, self.seq_num, self.ack_num)
                
            case States.SEND_SYN:
                self.sent_packet = packet
                self.state = States.AWAIT_S_A
                return packet
            
            case States.S_RECEIVED:
                self.recv_packet = packet
                self.state = States.AWAIT_S_A
                return Packet(Message("TEST"),Flags.SYN_ACK.value, self.seq_num, self.ack_num)
            case States.S_A_RECEIVED:
                self.recv_packet = packet
                self.state = States.AWAIT_A
                return Packet(Message("TEST"),Flags.ACK.value, self.seq_num, self.ack_num)
            case States.A_RECEIVED:
                self.recv_packet = packet
                self.state = States.EXECUTE
                return None
                            
            case States.AWAIT_S_A:
                if self.timeout:
                    self.retries += 1
                    if self.retries < RETRY_LIMIT:
                        self.timeout = False
                        return self.sent_packet #Resend Syn Packet
                    else:
                        self.sent_packet = None
                        self.recv_packet = None
                        self.retries = 0
                        self.timeout = False
                        self.state = States.CLOSED
                        return None
                else:
                    self.state = States.S_A_RECEIVED
                    return None
            case States.AWAIT_A:
                if self.timeout:
                    self.retries += 1
                    if self.retries < RETRY_LIMIT:
                        self.timeout = False
                        return self.sent_packet #Resend Syn/Ack Packet
                    else:
                        self.sent_packet = None
                        self.recv_packet = None
                        self.retries = 0
                        self.timeout = False
                        self.state = States.CLOSED
                        return None
                else:
                    self.state = States.A_RECEIVED
                    return None
                    
            case States.EXECUTE:
                # Execute command
                self.sent_packet = None
                self.recv_packet = None
                self.retries = 0
                self.timeout = False
                self.state = States.CLOSED
                return None
            
            case _:
                raise ValueError(f"Invalid state: {self.state}")
        
    def send_command(self, packet: Packet, drop=False):
        # Send a command to the balloon
        if drop:
            self.timeout = True
        
        self.state = States.SEND_SYN
        assert packet.flags == 2, "Packet must be a Syn packet in order to initiate communication" #Packet is Syn Packet
        return self.run(packet)
    
    def receive_packet(self, packet: Packet, drop=False): #add timeout here, returns boolean, packet
        # Receive a packet from the balloon
        if drop:
            self.timeout = True
        
        match packet.flags:
            case Flags.SYN.value:
                self.state = States.S_RECEIVED
            case Flags.SYN_ACK.value:
                self.state = States.S_A_RECEIVED
            case Flags.ACK.value:
                self.state = States.A_RECEIVED
            
        return self.run(packet)
    
    def trigger_timout(self):
        self.timeout = True
        self.retries += 1
        self.run(self.sent_packet)
        
    def drop_packet(self):
        pass