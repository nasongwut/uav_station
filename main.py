import serial,time,struct,base64,time,websocket,json

import _thread

STARTBIT = (0x55)
ENDBIT = (0x2e)
PACKETSIZE = struct.calcsize('iiiiiiiiiii')



SERIAL_PORT = serial.Serial(
    port="COM31",
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=0.1, 
)

time.sleep(1)


def write_serial(unpack):
    print('upload command')
    print(unpack)
    print(type(unpack))
    # print("write Serial")
    values = bytearray([unpack[0], unpack[1], unpack[2], unpack[3], unpack[4]])
    # STARTBIT = (0x55)
    SERIAL_PORT.write(STARTBIT.to_bytes(1, byteorder='big'))
    SERIAL_PORT.write(values[0].to_bytes(1, byteorder='big'))
    SERIAL_PORT.write(values[1].to_bytes(1, byteorder='big'))
    SERIAL_PORT.write(values[2].to_bytes(1, byteorder='big'))
    SERIAL_PORT.write(values[3].to_bytes(1, byteorder='big'))
    SERIAL_PORT.write(values[4].to_bytes(1, byteorder='big'))
    SERIAL_PORT.write(ENDBIT.to_bytes(1, byteorder='big')) 

def read_serial():
    # print("Read Serial")
    datas = SERIAL_PORT.read()
    for i in datas:
        if i == STARTBIT:

            data = SERIAL_PORT.read(PACKETSIZE)
            payload = base64.b64encode(data).decode('ascii')
            # print(payload)
            # unpack_st = struct.unpack('iiiiiiiiiii',data)
            # data_dict = {"src":unpack_st[0],
            #     "dst":unpack_st[1],
            #     "seq":unpack_st[2],
            #     "cmd":unpack_st[3],
            #     "sta":unpack_st[4],
            #     "motor_x":unpack_st[5],
            #     "motor_y":unpack_st[6],
            #     "sta_volt":unpack_st[7],
            #     "sta_amp":unpack_st[8],
            #     "uav_volt":unpack_st[9],
            #     "uav_amp":unpack_st[10]
            #     }
            # print('-------------------------')
            # print(payload)

            return payload





def on_message(ws, message):
    data = json.loads(message)
    if data['type']== 'uav':
        print('--------Command------')
        payload = data['bin']
        packet = base64.b64decode(payload)
        # unpack = struct.unpack('iiiiiiiiiii',packet)
        unpack = struct.unpack('iiiii',packet)
        # print(unpack)
        # print(type(unpack))
        write_serial(unpack)


    if data['type']== 'station':
        print('Command')



def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        while True:
            data = read_serial()
            upacket = {'type':'station','bin':data}
            # print(upacket)
            ws.send(json.dumps(upacket))
            time.sleep(0.1)
            
        # for i in range(3):
        #     time.sleep(1)
        #     ws.send("Hello %d" % i)
        # time.sleep(1)
        ws.close()
        print("thread terminating...")
    _thread.start_new_thread(run, ())


if __name__ == "__main__":
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:8000/ws/station100",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    ws.run_forever()










