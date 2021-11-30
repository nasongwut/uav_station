long randNumber;

uint8_t STARTBIT = 0x55;
uint8_t STOPBIT  = 0x99;
uint8_t PACKSIZE = 20;



typedef struct
{
  uint32_t  src=100; 
  uint32_t  dst=0;
  uint32_t   seq=0;
  uint32_t   cmd=0;
}packet_header;

typedef struct{
  packet_header h;
  uint32_t sta = 0;
  uint32_t sta_motor_x = 0;
  uint32_t sta_motor_y = 0;
  uint32_t sta_volt = 0;
  uint32_t sta_amp = 0;
  uint32_t uav_volt = 24.2*100;
  uint32_t uav_amp = 16000;
}packet_station_sta;

packet_station_sta packet; 

typedef struct{
  uint8_t src = 0;
  uint8_t dst = 0;
  uint8_t seq = 0;
  uint8_t command = 0;   /*0=idle,1=init,2=busy*/
  uint8_t uavtype = 0; /*1=S500,2=650,3=x8*/
}command_struct;


command_struct command; 

void setup() {
  Serial.begin(115200);
  Serial.write(byte(10));
}


void read_serial()  {
    while (Serial.available() > 0) {
      byte byteArray[5] = {};
      if (Serial.read() == 85){
        Serial.println("------------------------START RECORD------------------------");
        int rlen = Serial.readBytes(byteArray,5);
        for (int i=0;i<rlen;i++){
          Serial.println(byteArray[i]);
        }  
      }
    }
}
        
       
void write_serial(){
  randNumber = random(300);
  packet.sta = randNumber;
  Serial.write(0x55);
  Serial.write((const byte*)&packet, sizeof(packet));
  Serial.write(0x2e);
//  delay(1000);
}

void loop() {       
  write_serial();
  read_serial();
}
