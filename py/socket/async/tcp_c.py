import asyncio
import sys

addr = ('127.0.0.1', 1234)
if len(sys.argv) > 1:
    addr = (sys.argv[1], 1234)


async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection(*addr)

    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(1024)
    print(f'Received: {data.decode()!r}')

    writer.close()
    await writer.wait_closed()

asyncio.run(tcp_echo_client('Async TCP Client'))
