import asyncio, json,base64,struct,serial,time
from asyncio.windows_events import NULL
import websockets
from websockets.exceptions import ConnectionClosed
import random

FRAME_SYNC = b'\x55'
SERIAL_PORT = serial.Serial(
    port="COM6",
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=0.1, 
)
time.sleep(1)

uri = "ws://192.168.1.36:8000/ws/station001"

async def get_serial():
    size = struct.calcsize('HHHHHHHHHHH')
    payload =''
    # msg = ''
    msg =  SERIAL_PORT.read()
    if msg == FRAME_SYNC:
        msg =  SERIAL_PORT.read(size)



        ###TEMP####
        # temp = random.randrange(0, 20)
        # payload = base64.b64encode(temp).decode('ascii')

        
        payload = base64.b64encode(msg).decode('ascii')
        # print(payload)
    return payload

async def post_serial(command):

    print('--------------------------upload packet-------------------------------')
    send_command = json.loads(command)
    msg = send_command['bin']
    base64_bytes = msg.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    SERIAL_PORT.write(message_bytes)
    print('End Send------------------>>')
    return

async def connect(uri):
    async with websockets.connect(uri) as websocket:
        print("Connected to Websocket Server")
        while True:
            payload = await get_serial()

            # unpack_st = struct.unpack('HHHHHHHHHHH',payload)
            # print(unpack_st)

            # payload = base64.b64encode(msg).decode('ascii')


            msg = {'type':'Station','bin':NULL}

            ####################SEND STATION STATUS TO WEBSERVER####################
            if payload != "":
                msg = {'type':'Station','bin':payload}
                await websocket.send(json.dumps(msg))
            else:
                # print('NO DATA ')
                pass

            ####################RESIVE STATION STATUS TO WEBSERVER####################
            try:
                ws_sub = await asyncio.wait_for(websocket.recv(), timeout=0.05)
                if json.dumps(msg) != ws_sub :
                    await post_serial(ws_sub)
            except asyncio.TimeoutError:
                pass

async def main():
    while True:
        try:
            await connect(uri)
        except ConnectionClosed:
            await asyncio.sleep(2)
            print("Not able to connect.. Retying in 3 seconds")
            await connect(uri)
asyncio.get_event_loop().run_until_complete(main())



            # await asyncio.sleep(0.01)
            # if ws_sub != '':
            #     print(ws_sub)
            # if json.dumps(msg) != ws_sub :
            #     ws_sub_dict = json.loads(ws_sub)
            #     if ws_sub_dict['type'] == 'Station':
            #         print('command from uav')

            
                # print('NO DATA')
            # print(payload)

            #####################GET DATA FROM SERIAL#####################
            # data_serial = await get_serial()
            # byte_data = struct.pack('<IIIIIIIIII',
            #     data_serial['src'],
            #     data_serial['dst'],
            #     data_serial['seq'],
            #     data_serial['status'],
            #     data_serial['sta_mortor_x'],
            #     data_serial['sta_mortor_y'],
            #     data_serial['sta_charge'],
            #     data_serial['sta_volt_sta'],
            #     data_serial['uav_amp'],
            #     data_serial['uav_capacity'])

            # data = base64.b64encode(byte_data).decode('ascii')
            # msg = {'type':'Station','bin':data}
            # await websocket.send(json.dumps(msg))

            # # print(msg)
            # ws_sub = await websocket.recv()

            # if json.dumps(msg) != ws_sub :
            #     ws_sub_dict = json.loads(ws_sub)
            #     if ws_sub_dict['type'] == 'Station':
            #         print('command from uav')

            # await asyncio.sleep(0.05)

# async def main():

#     while True:
#         try:
#             await connect(uri)
#         except ConnectionClosed:
#             await asyncio.sleep(2)
#             print("Not able to connect.. Retying in 3 seconds")
#             await connect(uri)

# asyncio.get_event_loop().run_until_complete(main())