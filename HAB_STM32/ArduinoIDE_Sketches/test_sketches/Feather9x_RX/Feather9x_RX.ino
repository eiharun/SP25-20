// Feather9x_RX
// -*- mode: C++ -*-
// Example sketch showing how to create a simple messaging client (receiver)
// with the RH_RF95 class. RH_RF95 class does not provide for addressing or
// reliability, so you should only use RH_RF95 if you do not need the higher
// level messaging abilities.
// It is designed to work with the other example Feather9x_TX

#include <SPI.h>
#include <RH_RF95.h>
#include<Servo.h>

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

// instantiate servo object
Servo servo;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
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
  rf95.setSpreadingFactor(12);
  // rf95.setSignalBandwidth(12500);

  // new servo code
  /*
   * min (optional): the pulse width, in microseconds, corresponding to the minimum (0 degree) angle on the servo (defaults to 544)
   * max (optional): the pulse width, in microseconds, corresponding to the maximum (180 degree) angle on the servo (defaults to 2400)
   */
  servo.attach(PIN) // REPLACE WITH PIN WE USE, servo.attach(pin, min, max) is an alternative
  if (!servo.attached()) {
    Serial.print("Servo motor not connected");
  }
  Serial.print("Servo motor connected");
  
  servo.write(STARTING_ANGLE) // REPACE WITH STARTING ANGLE OF SERVO MOTOR
}

void loop() {
  if (rf95.available()) {
    // Should be a message for us now
    uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
    uint8_t len = sizeof(buf); 
    memset(buf, 0, sizeof(buf));
    if (rf95.recv(buf, &len)) {
      digitalWrite(RX_LED, HIGH);
      RH_RF95::printBuffer("Received: ", buf, len);
      Serial.print("Got: ");
      Serial.println((char*)buf);
       Serial.print("RSSI: ");
      Serial.println(rf95.lastRssi(), DEC);
      delay(50);
      digitalWrite(RX_LED, LOW);
      // Send a reply
      uint8_t data[RH_RF95_MAX_MESSAGE_LEN] = "ACK: ";
      strcpy(data+5, buf);
      digitalWrite(TX_LED, HIGH);
      rf95.send(data, strlen(data));
      rf95.waitPacketSent();
      Serial.println("Sent a reply");

      // Josh's Code for servo motor operation
      String message = (char*)buf;
      String command;
      for (int i = 0; i < 4 ; i++){
        command += message[i];
      }
      if (command == "vent"){
        uint8_t dur = message[message.length()];
        // open vent via servo
        // servo.write(angle)
        servo.write(60); // CHANGE ANGLE IF NEEDED        
        delay(dur); // allow time for servo movement
        // close vent
        servo.write(0);
      }
    } else {
      Serial.println("Receive failed");
    }
    delay(50);
    digitalWrite(TX_LED, LOW);
    delay(50);
    digitalWrite(TX_LED, HIGH);
    digitalWrite(RX_LED, HIGH);
    delay(400);
    digitalWrite(TX_LED, LOW);
    digitalWrite(RX_LED, LOW);

  }
}
