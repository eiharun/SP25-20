// Feather9x_TX
// -*- mode: C++ -*-
// Example sketch showing how to create a simple messaging client (transmitter)
// with the RH_RF95 class. RH_RF95 class does not provide for addressing or
// reliability, so you should only use RH_RF95 if you do not need the higher
// level messaging abilities.
// It is designed to work with the other example Feather9x_RX

#include <SPI.h>
#include <RH_RF95.h>

#define RFM95_RST 4  // 
#define RFM95_CS  3  // 
#if defined(__AVR_ATmega328P__)
  #define RFM95_INT 2  // 
#else
  #define RFM95_INT 0  // 
#endif

#if defined(__AVR_ATmega328P__)
  #define TX_LED      8
  #define RX_LED      7
#else
  #define TX_LED      A5
  #define RX_LED      A6
#endif
// Change to 434.0 or other frequency, must match RX's freq!
#define RF95_FREQ 915.0

// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);
unsigned long latencies[255];

void setup() {
  digitalWrite(TX_LED, HIGH);
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
  rf95.setSpreadingFactor(12);
  rf95.setSignalBandwidth(125000);
  #define RX_TIMEOUT 15000
  #define DELAY_TX 1500
  digitalWrite(TX_LED, LOW);
}

int16_t packetnum = 0;  // packet counter, we increment per xmission

void loop() {
  Serial.println("Transmitting..."); // Send a message to rf95_server

  char radiopacket[16] = "Sending #      ";
  packetnum = (packetnum+1)%99999;
  itoa(packetnum, radiopacket+9, 10);
  Serial.print("Sending: "); Serial.println(radiopacket);
  radiopacket[19] = 0;

  Serial.println("Sending...");
  unsigned long start = millis();
  digitalWrite(TX_LED, HIGH);
  delay(10);
  rf95.send((uint8_t *)radiopacket, 16);

  Serial.println("Waiting for packet to complete...");
  delay(10);
  rf95.waitPacketSent();

  digitalWrite(TX_LED, LOW);
  // Now wait for a reply
  uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
  uint8_t len = sizeof(buf);

  Serial.println("Waiting for reply...");
  if (rf95.waitAvailableTimeout(RX_TIMEOUT)) {
    unsigned long end = millis();
    // Should be a reply message for us now
    if (rf95.recv(buf, &len)) {
      digitalWrite(RX_LED, HIGH);
      Serial.print("Got reply: ");
      Serial.println((char*)buf);
      Serial.print("\tRSSI: ");
      Serial.println(rf95.lastRssi(), DEC);
      Serial.print("\tSNR: ");
      Serial.println(rf95.lastSNR(), DEC);
      Serial.print("\tLatency: ");
      latencies[packetnum%255] = end-start;
      Serial.println(end-start);
      if (packetnum >= 255){
        float sum=0;
        for(int i=0; i<255; i++){
          sum += latencies[i];
        }
        float average=sum/255;
        
        Serial.print("Average Latency past 255 messages: ");
        Serial.println(average);
      }
    } else {
      Serial.println("Receive failed");
    }
  } else {
    Serial.println("No reply, is there a listener around?");
  }
  delay(DELAY_TX);
  digitalWrite(RX_LED, LOW);

}
