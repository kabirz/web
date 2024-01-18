import asyncio


async def handle_echo(reader, writer):
    writer.write(b'ASync TCP Server')
    await writer.drain()

    data = await reader.read(1024)
    addr = writer.get_extra_info('peername')
    print(f'{addr}: {data.decode()}')

    writer.close()


async def main():
    async with await asyncio.start_server(handle_echo, '0.0.0.0', 1234) as server:
        await server.serve_forever()

asyncio.run(main())
