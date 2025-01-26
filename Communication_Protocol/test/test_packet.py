from protocol import Packet, Message

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