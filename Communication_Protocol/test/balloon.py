import socket
# from protocol import *

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', 12346))
seq=0
while True:
    recv, addr = sock.recvfrom(1024)
    print("Recieved: ", recv)
    if recv[0] == 1:
        ack = (int(recv[1])+1).to_bytes(1, byteorder='big')
        seq+=1
        seq_b = (seq).to_bytes(1, byteorder='big')
        print("Sent SYN-ACK")
        sock.sendto(b"\x03"+seq_b+ack+recv[-1].to_bytes(1,'big'), addr)
    elif recv[0] == 2:
        sock.sendto(b"EXE", addr)
        print("EXE")#ON BALOON EXECUTE COMMAND
        seq=0
        
    