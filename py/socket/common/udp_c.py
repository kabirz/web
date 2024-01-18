import socket
import sys

addr = ('127.0.0.1', 5678)
if len(sys.argv) > 1:
    addr = (sys.argv[1], 5678)
s = socket.socket(type=socket.SOCK_DGRAM)
s.sendto(b'UDP client send', addr)
ret, addr = s.recvfrom(1024)
print(f'{addr}: {ret.decode()}')
s.close()
