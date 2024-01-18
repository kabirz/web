import socket
import sys

s = socket.socket()
addr = ('127.0.0.1', 1234)
if len(sys.argv) > 1:
    addr = (sys.argv[1], 1234)

s.connect(addr)
buf = s.recv(1024)
print(f'{addr}: {buf.decode()}')
s.send(f'receive:{buf.decode()}'.encode())
s.close()
