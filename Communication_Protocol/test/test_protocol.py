import pytest
from protocol import *

def test_protocol():
    GroundStation = Protocol()
    Balloon = Protocol()
    
    p1 = Packet(Message("OPEN", "1"), 2, 0, 0)
    p1syn = GroundStation.send_command(p1)
    
    p1synack = Balloon.receive_packet(p1syn, drop=False)
    
    p1ack = GroundStation.receive_packet(p1synack, drop=False) #Ground Station assumes communication is closed now
    
    Balloon.receive_packet(p1ack, drop=False) #Balloon assumes communication is closed
    
def test_synack_drop():
    GroundStation = Protocol()
    Balloon = Protocol()
    
    p1 = Packet(Message("OPEN", "1"), 2, 0, 0)
    while True:
        p1syn = GroundStation.send_command(p1, drop=False)#p1syn = p1 
        p1synack = Balloon.receive_packet(p1syn, drop=False)
        
        p1ack = GroundStation.receive_packet(p1synack, drop=True) #syn ack does not reach ground station in time
        
        Balloon.receive_packet(p1ack, drop=False) #Balloon assumes communication is closed