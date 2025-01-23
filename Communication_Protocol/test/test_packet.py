from protocol import Packet, Message

def compute_checksum(header: bytes):
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

def test_open1_packet_construct():
    packet1 = Packet(0, 0, 0, Message("OPEN", "1"))
    assert packet1.seq == 0
    assert packet1.ack == 0
    assert packet1.rep == 0
    assert packet1.payload == b"\x40\x01\x01"
    checksum = compute_checksum(b"EXMP\x00\x00\x00\x00\x00\x00")
    assert packet1.construct_packet() == b"EXMP\x00\x00\x00\x00\x00\x00"+checksum+b"\x40\x01\x01"
    

##

