import socket
# from protocol import *

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', 12345))
BALOON_PORT=12346

# 1 - SYN; 2 - ACK; 3 - SYN-ACK 
# Seq#
# Ack#

iter=0
while True: 
    iter+=1
    in_ = input("")
    sock.sendto(b"\x01\x01\x00"+iter.to_bytes(1,'big'), ('localhost', BALOON_PORT))  
    print("Sent SYN")  
    seq=1
    recv, addr = sock.recvfrom(1024)
    print("Recieved: ", recv)
    if recv[0]== 1:#SYN
        ack = (int(recv[1])+1).to_bytes(1, byteorder='big')
        seq+=1
        seq_b = (seq).to_bytes(1, byteorder='big')
        print("Sent SYN-ACK")
        sock.sendto(b"\x03"+seq_b+ack+iter.to_bytes(1,'big'), addr)    
    elif recv[0] == 2:#ACK
        pass#DO NOTHING
    elif recv[0] == 3:#SYN-ACK
        seq+=1
        seq_b = (seq).to_bytes(1, byteorder='big')
        ack = (int(recv[1])+1).to_bytes(1, byteorder='big')
        print("Sent ACK")
        sock.sendto(b"\x02"+seq_b+ack+iter.to_bytes(1,'big'), addr)