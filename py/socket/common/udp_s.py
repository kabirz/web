import socket

s = socket.socket(type=socket.SOCK_DGRAM)
s.bind(('0.0.0.0', 5678))

for _ in range(3):
    ret, addr = s.recvfrom(1024)
    if ret:
        print(f'{addr}: {ret.decode()}')
        s.sendto(b'UDP server', addr)


s.close()
