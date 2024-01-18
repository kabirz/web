import socket

s = socket.socket()

s.bind(('0.0.0.0', 1234))

s.listen(3)

for _ in range(3):
    cs, addr = s.accept()
    cs.send(b'Tcp server')
    buf = cs.recv(1024)
    print(f'{addr}: {buf.decode()}')


s.close()
