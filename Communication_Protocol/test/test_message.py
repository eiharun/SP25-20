import pytest
from protocol import Message

#TEST TLV ENCODING 
def test_open1_message_encode():
    message = Message("OPEN", "1")
    assert message.command.name == "OPEN"
    assert message.command.value == 64
    assert message.data == 1
    assert message.length == 1
    assert message.payload == None
    encoded_msg = message.encode()
    #b01000000-00000001-00000001
    assert encoded_msg == b"\x40\x01\x01"
    assert bin(message.payload) == '0b10000000000000100000001'
    
def test_open275_message_encode():
    message = Message("OPEN", "275")
    assert message.command.name == "OPEN"
    assert message.command.value == 64
    assert message.data == 275
    assert message.length == 2
    assert message.payload == None
    encoded_msg = message.encode()
    #b01000000-00000010-00000001-00010011
    assert encoded_msg == b"\x40\x02\x01\x13"
    assert bin(message.payload) == '0b1000000000000100000000100010011'
    
def test_emptyopen_message_encode():
    with pytest.raises(ValueError):
        message = Message("OPEN")
        assert message.command.name == "OPEN"
        assert message.command.value == 64
        assert message.data == None
        assert message.length == 0
        assert message.payload == None
        encoded_msg = message.encode()
        
def test_idle_message_encode():
    message = Message("IDLE")
    assert message.command.name == "IDLE"
    assert message.command.value == 0
    assert message.data == None
    assert message.length == 0
    assert message.payload == None
    encoded_msg = message.encode()
    #b00000000-00000000
    assert encoded_msg == b"\x00\x00"
    assert bin(message.payload) == '0b0'
    
def test_cutdown_message_encode():
    message = Message("CUTDOWN")
    assert message.command.name == "CUTDOWN"
    assert message.command.value == 1
    assert message.data == None
    assert message.length == 0
    assert message.payload == None
    encoded_msg = message.encode()
    #b00000001-00000000
    assert encoded_msg == b"\x01\x00"
    assert bin(message.payload) == '0b100000000'
    
