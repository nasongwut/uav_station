import websocket,serial,base64,struct,time,json
import _thread,base64

FRAME_SYNC = b'\x55'
STOP_SYNC = b'\x2e'
SERIAL_PORT = serial.Serial(
    port="COM21",
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=0.1, 
)
time.sleep(1)

def get_serial():
    size = struct.calcsize('iiiiiiiiiii')
    payload =''
    msg =  SERIAL_PORT.read()
    if msg == FRAME_SYNC:
        msg =  SERIAL_PORT.read(size)    
        payload = base64.b64encode(msg).decode('ascii')
    return payload

def post_serial():
    START = 85
    BYTESTOP = 90
    values = bytearray([255, 2, 3, 4, 5])
    SERIAL_PORT.write(bytes([START]))
    for i in values:
        SERIAL_PORT.write(bytes([i]))
        # time.sleep(0.001)
    print('----------------SEND----------------')
    
    return

def on_message(ws, message):
    # print('---------------------income msg'--------------------')
    pass #print(message)


def on_error(ws, error):
    pass #print(error)

def on_close(ws, close_status_code, close_msg):
    pass #print("### closed ###")

def on_open(ws):
    def th1run(*args):
        print('THREAD 1 is run')
        while True:
            sta_state = get_serial()
            if sta_state != "":
                msg = {'type':'Station','bin':sta_state}
                packet = json.dumps(msg)
                # print(packet)
                ws.send(packet)
                _thread.start_new_thread(th2run, ())
                # time.sleep(0.001)
        time.sleep(1)
        ws.close()
        print("thread terminating...")
    def th2run(*args):
        while True:
            # print("THREAD 2 is run")
            post_serial()
            pass
        # time.sleep(1)


    _thread.start_new_thread(th1run, ())
    

if __name__ == "__main__":
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:8000/ws/stationHarn",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    ws.run_forever()
