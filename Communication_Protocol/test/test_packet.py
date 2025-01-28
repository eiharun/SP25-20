from protocol import Packet, Message
from .fixtures import *
import pytest

def compute_checksum(msg, flags, seq, ack):
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

def test_open1_packet_construct():
    p = Packet(Message("OPEN", "1"), 0, 0, 0)
    assert p.flags == 0
    assert p.seq == 0
    assert p.ack == 0
    assert p.msg == (b"\x40",b"\x01",b"\x01\x03\x03\x03")
    checksum = compute_checksum(p.msg,p.flags,p.seq,p.ack)
    assert p.construct_packet() == [
        b"EXMP", #Callsign
        b"\x00\x00", #Flags
        b"\x00", #Sequence
        b"\x00", #Acknowledgement
        b"\x40", #Command
        b"\x01", #Length
        checksum, #Checksum
        b"\x01\x03\x03\x03" #Data
    ]
    
def test_open275_packet_construct():
    p = Packet(Message("OPEN", "275"), 0, 0, 0)
    assert p.flags == 0
    assert p.seq == 0
    assert p.ack == 0
    assert p.msg == (b"\x40",b"\x02",b"\x01\x13\x02\x02")
    checksum = compute_checksum(p.msg,p.flags,p.seq,p.ack)
    assert p.construct_packet() == [
        b"EXMP", #Callsign
        b"\x00\x00", #Flags
        b"\x00", #Sequence
        b"\x00", #Acknowledgement
        b"\x40", #Command
        b"\x02", #Length
        checksum, #Checksum
        b"\x01\x13\x02\x02" #Data
    ]
    
## Refer to test_cases.excalidraw.png for a visual representation of the test cases below

#Test Cases: (Default packet = OPEN 1)
# 1. Send packet to balloon, balloon recieves and sends back an SYN/ACK, ground station recieves SYN/ACK, and sends ACK, balloon recieves ACK. Perfect scenario.
# 2. Send packet to balloon, balloon recieves and sends back an SYN/ACK, ground station recieves SYN/ACK, and sends ACK, balloon does not recieve ACK, retransmits SYN/ACK, ground station recieves SYN/ACK, resends ACK, balloon recieves ACK.
# 3. TODO..... (more test cases)

# @pytest.mark.asyncio
# @pytest.mark.parametrize("setup_communication", [{"packet_loss_rate": 0.0, "latency_range": (1, 5)}], indirect=True)
# async def test_communication(setup_communication):
#     ground_station, balloon, channel = setup_communication

#     # Simulate a message with sequence number and content
#     packet = ground_station.create_packet(seq_num=1, msg="Hello, Balloon!")

#     # Send the packet and wait for an acknowledgment
#     try:
#         transmitted_packet = await ground_station.send_packet(packet)
#         assert transmitted_packet, "Packet transmission failed"
#         # Now, Balloon receives the packet
#         received_packet = balloon.receive_packet(transmitted_packet)
#         assert received_packet, "Balloon failed to receive the packet"
#         print("Test completed successfully!")
#     except TimeoutError as e:
#         print(str(e))
#         assert False, "Test failed due to timeout"

import pytest
import asyncio

@pytest.mark.asyncio
async def test_communication_protocol():
    # Setup the communication objects
    channel = CommunicationChannel(packet_loss_rate=0.1, latency_range=(0.1, 0.5))
    ground_station = GroundStation("Ground Station", channel)
    balloon = Balloon("Balloon")

    # Create and send a SYN packet
    packet = ground_station.create_packet(msg="SYN")
    try:
        # Send the packet and wait for acknowledgment
        ack_packet = await ground_station.send_packet(packet)
        assert ack_packet is not None, "Failed to receive ACK packet"
        print(f"Communication successful with seq={packet.seq} ack={ack_packet.ack}")
    except TimeoutError as e:
        assert False, str(e)
