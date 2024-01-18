import socket
import threading


def process_client_data(s: socket.socket, addr):
    data = s.recv(1024)
    print(f'{addr}: {data.decode()}')
    s.close()


s = socket.socket()
s.bind(('0.0.0.0', 1234))
s.listen(3)

for _ in range(3):
    cs, addr = s.accept()
    cs.send(b'Tcp server')
    threading.Thread(target=process_client_data, args=(cs, addr)).start()


s.close()
