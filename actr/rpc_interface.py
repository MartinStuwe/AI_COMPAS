import json
import asyncio
import aiofiles

# actions
async def send(writer, message):
    m = message + chr(4)
    print("MESSAGE IS: " + message)
    writer.write(m.encode('utf-8'))
    await writer.drain()  # Ensure the message is sent properly

async def receive(reader):
    buffer = ''
    while not chr(4) in buffer:
        data = await reader.read(1)  # Read one byte at a time
        buffer += data.decode('utf-8')
    
    json_data = buffer[:-1]  # Parse all except the end character
    return json.loads(json_data)

async def communicate(message):
    try:
        async with aiofiles.open("/home/scifaipy/act-r-port-num.txt", 'r') as f:
            port = int(await f.readline())
        
        async with aiofiles.open("/home/scifaipy/act-r-address.txt", 'r') as f:
            host = await f.readline()
            host = host.strip()  # Remove newline characters

        print("REACHED1")
        print(host)
        print(port)
        try:
            print("REACHED CONNECT")
            reader, writer = await asyncio.open_connection(host, 2651)
            print("REACHED CONNECTED")
        except asyncio.TimeoutError:
            print("Connection timed out")
        except ConnectionRefusedError:
            print("Connection refused by the server")
        except Exception as e:
            print(f"Failed to connect: {e}")
        print("Connection successfully established")

        await send(writer, message)
        print("REACHED3")
    
    except Exception as e:
        print(f"Failed to connect or send: {e}")
    
    finally:
        try:
            writer.close()
            await writer.wait_closed()  # Properly wait for the writer to be closed
            print("Connection closed.")
        except Exception as e:
            print(f"Error in closing connection: {e}")