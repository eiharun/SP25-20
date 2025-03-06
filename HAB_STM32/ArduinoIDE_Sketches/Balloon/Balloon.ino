#include <SPI.h>
#include <RH_RF95.h>

#define RFM95_RST 4  
#define RFM95_CS  3  
#define RFM95_INT 0  
#define TX_LED      A5
#define RX_LED      A6

#define RF95_FREQ 915.0
#define RX_TIMEOUT 5000

// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);

char radiopacket[20] = "";

void setup() {
  pinMode(RFM95_RST, OUTPUT);
  pinMode(TX_LED, OUTPUT);
  pinMode(RX_LED, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);

  Serial.begin(115200);
  while (!Serial) delay(1);
  delay(100);

  Serial.println("LoRa RX Test!");

  // manual reset
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);

  while (!rf95.init()) {
    Serial.println("LoRa radio init failed");
    while (1);
  }
  Serial.println("LoRa radio init OK!");

  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM
  if (!rf95.setFrequency(RF95_FREQ)) {
    Serial.println("setFrequency failed");
    while (1);
  }
  Serial.print("Set Freq to: "); Serial.println(RF95_FREQ);

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
  radiopacket[0] = 1;
  radiopacket[1] = 0;
  radiopacket[2] = 0;
  radiopacket[3] = 194;
  radiopacket[6] = 255;
}

int16_t packetnum = 0;  // packet counter, we increment per xmission
bool resend = false;
bool gotsyn = false;
bool gotsynack = false;

void loop() {
  // delay(1000); // Wait 1 second between transmits, could also 'sleep' here!

  /*Simplified Packet format: 
   * First Byte:  2 SYN; 1 ACK; 3 SYN/ACK
   * Second Byte: Seq #
   * Third Byte:  Ack #
   * Fourth Byte: Tag (i.e. command #) 0 IDLE; 1 CUTDOWN; 64 OPEN (x seconds); 194 TEST
   * Fifth Byte:  Data Length (n)
   * Sixth Byte:  Checksum (for now disable checking)
   * 6+nth Byte:  Data Payload 
   */
  

  if(rf95.waitAvailableTimeout(RX_TIMEOUT)){
    uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
    uint8_t len = sizeof(buf); 

    if (rf95.recv(buf, &len)) {
      digitalWrite(RX_LED, HIGH);
      RH_RF95::printBuffer("Received: ", buf, len);
       Serial.print("RSSI: ");
      Serial.println(rf95.lastRssi(), DEC);
      delay(50);
      digitalWrite(RX_LED, LOW);
    } else {
      Serial.println("Receive failed");
    }

    if (buf[0]==2){
      gotsyn = true;
      char data[10] = "ACKwtele";
      size_t data_len;
      
      radiopacket[4] = (char)data_len;
      memcpy(radiopacket + 6, data, 10);

      digitalWrite(TX_LED, HIGH);
      rf95.send((uint8_t *)radiopacket, 20);
      rf95.waitPacketSent();
      Serial.println("Sent ACK");
      digitalWrite(TX_LED, LOW);
    } else if (buf[0]==3){
      gotsynack = true;
      Serial.println("Recieved SYN/ACK");
    }

  }
  else{
    if(gotsyn && !gotsynack){
      /*Resend ack*/
      Serial.println("Missed SYN/ACK");
      digitalWrite(TX_LED, HIGH);
      radiopacket[1]++;
      rf95.send((uint8_t *)radiopacket, 20);
      rf95.waitPacketSent();
      Serial.println("Resent ACK");
      digitalWrite(TX_LED, LOW);
    }
  }
  if(gotsyn && gotsynack){
    digitalWrite(TX_LED, HIGH);
    digitalWrite(RX_LED, HIGH);
    delay(500);
    gotsyn = false;
    gotsynack = false;
    digitalWrite(TX_LED, LOW);
    digitalWrite(RX_LED, LOW);
    delay(500);
    digitalWrite(TX_LED, HIGH);
    digitalWrite(RX_LED, HIGH);
    delay(500);
    digitalWrite(TX_LED, LOW);
    digitalWrite(RX_LED, LOW);
  }

}
