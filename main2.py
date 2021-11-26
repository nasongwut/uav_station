import websocket,serial,base64,struct,time,json
import _thread



FRAME_SYNC = b'\x55'
SERIAL_PORT = serial.Serial(
    port="COM20",
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=0.1, 
)
time.sleep(1)

def get_serial():
    size = struct.calcsize('HHHHHHHHHHH')
    payload =''
    msg =  SERIAL_PORT.read()
    if msg == FRAME_SYNC:
        msg =  SERIAL_PORT.read(size)

        # print('DECODE')
        # print(msg)
        unpack_st = struct.unpack('HHHHHHHHHHH',msg)
        print(unpack_st)        
        payload = base64.b64encode(msg).decode('ascii')
        print('----payload-----')
        print(payload)
    return payload


async def post_serial(command):
    print('--------------------------upload packet-------------------------------')
    send_command = json.loads(command)
    msg = send_command['bin']
    base64_bytes = msg.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    SERIAL_PORT.write(message_bytes)
    print(msg)
    print('End Send------------------>>')
    return

def on_message(ws, message):
    # print('---------------------income msg'--------------------')
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        while True:
            sta_state = get_serial()
            if sta_state != "":
                msg = {'type':'Station','bin':sta_state}
                packet = json.dumps(msg)
                ws.send(packet)
                time.sleep(0.001)
            # print(packet)
            # time.sleep(0.1)
            

        # for i in range(3):
        #     time.sleep(1)
        #     ws.send("Hello %d" % i)
        time.sleep(1)
        ws.close()
        print("thread terminating...")
    _thread.start_new_thread(run, ())

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://192.168.1.36:8000/ws/stationHarn",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever()