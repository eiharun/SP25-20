# Protocol Requirements

    - Reliable communication (ack system)
    - Half-duplex communication **** LORA IS HALF DUPLEX - ONLY ONE DEVICE CAN TRANSMIT AT A TIME
    - Error detection
    - Forward Error correction **** FEC IS BUILT INTO LORA
        - Repetition
        - Codeword + hamming distance
    - Low Data Rate (small packets)
    - Support for future expandability

Packet Structure:

```plaintext

+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           Callsign                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
0                   1                   2                   3
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 bits
            1               2               3               4 bytes
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       Sequence Number        |       Acknowledgement Number   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|             Type             |           Checksum             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                            Data                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

Sequence Number: 8 bits
    Used to keep track of packets sent and received

Acknowledgement Number: 8 bits
    Used to acknowledge packets received

Type: Protocol Type (include rep#?)
    Command - includes SYN/ACK flags for connection (similar to TCP)
    Telemetry - Best effort (like UDP)
    Idle - 0x00 (no data) only sends periodically to keep connection alive (or can be sent by balloon to sense if balloon is in range)

Checksum: Ensures packet header integrity

Data: TLV (Tag, Length, Value)
    Tag = Command - 1 byte
    Length = Length of Value - 1 byte
    Value = Data - `Length` bytes



---

| Callsign |
| Seq # | Ack # | Type | Checksum |
| Tag/Command | Length | Value |

---

```

Sequence and Acknowledgement Numbers are 0x00 only if it is not being used. Sequence and Acknowledgement cannot both be 0x00 only one or the other.

Ack number = incoming sequence number
Seq number = outgoing sequence number which is incremented by 1 every retranmission

Every new packet will have seq number 0x01

If two packets are recieved with same seq number. They are treated as seperate commands
