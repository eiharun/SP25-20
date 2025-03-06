#include <SPI.h>
#include <RH_RF95.h>

#define RFM95_RST 4
#define RFM95_CS 3
#define RFM95_INT 0
#define TX_LED A5
#define RX_LED A6

#define RF95_FREQ 915.0
#define RX_TIMEOUT 5000

// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);
unsigned long latencies[255];
char radiopacket[20] = "";

void setup() {
  pinMode(RFM95_RST, OUTPUT);
  pinMode(TX_LED, OUTPUT);
  pinMode(RX_LED, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);

  Serial.begin(115200);
  while (!Serial) delay(1);
  delay(100);

  Serial.println("LoRa TX Test!");

  // manual reset
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);

  while (!rf95.init()) {
    Serial.println("LoRa radio init failed");
    while (1)
      ;
  }
  Serial.println("LoRa radio init OK!");

  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM
  if (!rf95.setFrequency(RF95_FREQ)) {
    Serial.println("setFrequency failed");
    while (1)
      ;
  }
  Serial.print("Set Freq to: ");
  Serial.println(RF95_FREQ);

  // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on

  // The default transmitter power is 13dBm, using PA_BOOST.
  // If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then
  // you can set transmitter powers from 5 to 23 dBm:
  rf95.setTxPower(23, false);
  rf95.setSpreadingFactor(7);
  // rf95.setSignalBandwidth(12500);
  
  if (!rf95.printRegisters()) {
    Serial.println("printRegisters failed");
    while (1);
  }

  radiopacket[0] = 2;
  radiopacket[1] = 0;
  radiopacket[2] = 0;
  radiopacket[3] = 194;
  radiopacket[6] = 255;

}

int16_t packetnum = 0;  // packet counter, we increment per xmission
bool resend = false;

void loop() {
  delay(1000);                        // Wait 1 second between transmits, could also 'sleep' here!
  Serial.println("Type data (under 10 char)");  // Send a message to rf95_server

  char input[10]="";
  while(input[0]==0){
    Serial.println("IDLE");
    Serial.readBytesUntil('\n', input, 10);
    uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
    uint8_t len = sizeof(buf);
    if (rf95.waitAvailableTimeout(RX_TIMEOUT)) {
      // Should be a reply message for us now
      if (rf95.recv(buf, &len)) {
        digitalWrite(RX_LED, HIGH);
        RH_RF95::printBuffer("Received: ", buf, len);
        Serial.print("RSSI: ");
        Serial.println(rf95.lastRssi(), DEC);
      } else {
        Serial.println("Receive failed");
      }
      if(buf[0]==1){
        radiopacket[7] = 0;
        radiopacket[0] = 3;
        radiopacket[2] = buf[3]+1;

        Serial.println("Sending SYN/ACK...");
        digitalWrite(TX_LED, HIGH);
        delay(10);
        rf95.send((uint8_t *)radiopacket, 20);

        // Serial.println("Waiting for packet to complete...");
        delay(10);
        rf95.waitPacketSent();
      }
    } 
  }
  /*Simplified Packet format: 
   * First Byte:  2 SYN; 1 ACK; 3 SYN/ACK
   * Second Byte: Seq #
   * Third Byte:  Ack #
   * Fourth Byte: Tag (i.e. command #) 0 IDLE; 1 CUTDOWN; 64 OPEN (x seconds); 194 TEST
   * Fifth Byte:  Data Length (n)
   * Sixth Byte:  Checksum (for now disable checking)
   * 6+nth Byte:  Data Payload 
   */
  char data[10]="TEST";
  int data_len=4;
  // while (Serial.available()) {
  // }
  Serial.println("Sending...");
  unsigned long start = millis();
  
  radiopacket[4] = (char)data_len;
  memcpy(radiopacket + 6, data, 10);
  radiopacket[0] = 2;
  radiopacket[19] = 0;

  digitalWrite(TX_LED, HIGH);
  delay(10);
  rf95.send((uint8_t *)radiopacket, 20);

  // Serial.println("Waiting for packet to complete...");
  delay(10);
  rf95.waitPacketSent();
  

  digitalWrite(TX_LED, LOW);
  // Now wait for a reply
  uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
  uint8_t len = sizeof(buf);
  Serial.println("Waiting for reply ACK...");
  if (rf95.waitAvailableTimeout(RX_TIMEOUT)) {
    // Should be a reply message for us now
    if (rf95.recv(buf, &len)) {
      digitalWrite(RX_LED, HIGH);
      RH_RF95::printBuffer("Received: ", buf, len);
      Serial.print("RSSI: ");
      Serial.println(rf95.lastRssi(), DEC);
    } else {
      Serial.println("Receive failed");
    }
  } else {
    Serial.println("No reply, resending [TODO]");
    resend = true;
  }
  digitalWrite(RX_LED, LOW);
  delay(50);
  if (!resend) {
    radiopacket[7] = 0;
    radiopacket[0] = 3;
    radiopacket[2] = buf[3]+1;

    Serial.println("Sending SYN/ACK...");
    digitalWrite(TX_LED, HIGH);
    delay(10);
    rf95.send((uint8_t *)radiopacket, 20);

    // Serial.println("Waiting for packet to complete...");
    delay(10);
    rf95.waitPacketSent();
    digitalWrite(TX_LED, LOW);
  }
  else{
    int cnt=0;
    while(resend){
      radiopacket[0] = 2;
      radiopacket[1]++;

      Serial.print("Resending... #");
      Serial.println(cnt);
      digitalWrite(TX_LED, HIGH);
      delay(10);
      rf95.send((uint8_t *)radiopacket, 20);

      // Serial.println("Waiting for packet to complete...");
      delay(10);
      rf95.waitPacketSent();
      digitalWrite(TX_LED, LOW);
      uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
      uint8_t len = sizeof(buf);
      Serial.println("Waiting for ACK resend...");
      if (rf95.waitAvailableTimeout(RX_TIMEOUT)) {
        // Should be a reply message for us now
        if (rf95.recv(buf, &len)) {
          digitalWrite(RX_LED, HIGH);
          RH_RF95::printBuffer("Received: ", buf, len);
          Serial.print("RSSI: ");
          Serial.println(rf95.lastRssi(), DEC);
        } else {
          Serial.println("Receive failed");
        }
        digitalWrite(RX_LED, LOW);

        radiopacket[0] = 3;
        radiopacket[2] = buf[3]+1;
        radiopacket[7] = 0;

        Serial.println("Sending SYN/ACK...");
        digitalWrite(TX_LED, HIGH);
        delay(10);
        rf95.send((uint8_t *)radiopacket, 20);

        // Serial.println("Waiting for packet to complete...");
        delay(10);
        rf95.waitPacketSent();
        digitalWrite(TX_LED, LOW);
        resend = false;
      } else {
        Serial.println("No reply, resending [TODO]");
        resend = true;
      }
      if(cnt>=10){
        break;
      }
      cnt++;
    }
    if(resend){
      Serial.println("Exceeded retries");
    }
    
  }
  unsigned long end = millis();





  // /*Latency Calculation*/
  float average;
  Serial.print("Latency: ");
  latencies[packetnum%255] = end-start;
  Serial.print(end-start);
  Serial.println("ms");
  if (packetnum >= 255){
    float sum=0;
    for(int i=0; i<255; i++){
      sum += latencies[i];
    }
    average=sum/255;
    Serial.print("Average Latency: ");
    Serial.println(average);
  }

  delay(50);
  digitalWrite(RX_LED, LOW);
}
