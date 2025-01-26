import pytest
from protocol import Message

def unpad(data: bytes):
    """
    Unpads the data to a 4 byte boundary PKCS#7, with error checking
    """
    if len(data) == 0 or len(data) % 4 != 0:
        raise ValueError("Invalid data length for PKCS#7 padding")

    padding_len = data[-1]
    if padding_len == 0 or padding_len > 4:
        raise ValueError("Invalid padding length")

    if data[-padding_len:] != bytes([padding_len]) * padding_len:
        raise ValueError("Invalid padding")

    return data[:-padding_len]

#TEST TLV ENCODING 
def test_open1_message_encode():
    message = Message("OPEN", "1")
    assert message.command.name == "OPEN"
    assert message.command.value == 64
    assert message.data == 1
    assert message.length == 1
    msg = message.get_bytes()
    msg_cmd,msg_len,msg_data = msg
    #b01000000-00000001-00000001
    assert msg == (b"\x40",b"\x01",b"\x01\x03\x03\x03")
    assert msg_cmd == b"\x40"
    assert msg_len == b"\x01"
    assert msg_data == b"\x01\x03\x03\x03"
    assert unpad(msg_data) == b"\x01"
    
def test_open275_message_encode():
    message = Message("OPEN", "275")
    assert message.command.name == "OPEN"
    assert message.command.value == 64
    assert message.data == 275
    assert message.length == 2
    msg = message.get_bytes()
    msg_cmd,msg_len,msg_data = msg
    #b01000000-00000010-00000001-00010011
    assert msg == (b"\x40",b"\x02",b"\x01\x13\x02\x02")
    assert msg_cmd == b"\x40"
    assert msg_len == b"\x02"
    assert msg_data == b"\x01\x13\x02\x02"
    
def test_emptyopen_message_encode():
    with pytest.raises(ValueError):
        message = Message("OPEN") #Open command, and BCD encoded commands require a data field
        
def test_idle_message_encode():
    message = Message("IDLE")
    assert message.command.name == "IDLE"
    assert message.command.value == 0
    assert message.data == None
    assert message.length == 0
    msg = message.get_bytes()
    msg_cmd,msg_len,msg_data = msg
    #b00000000-00000000
    assert msg == (b"\x00",b"\x00", b"")
    assert msg_cmd == b"\x00"
    assert msg_len == b"\x00"
    assert msg_data == b""
    
def test_cutdown_message_encode():
    message = Message("CUTDOWN")
    assert message.command.name == "CUTDOWN"
    assert message.command.value == 1
    assert message.data == None
    assert message.length == 0
    msg = message.get_bytes()
    msg_cmd,msg_len,msg_data = msg
    #b00000001-00000000
    assert msg == (b"\x01",b"\x00", b"")
    assert msg_cmd == b"\x01"
    assert msg_len == b"\x00"
    assert msg_data == b""    
