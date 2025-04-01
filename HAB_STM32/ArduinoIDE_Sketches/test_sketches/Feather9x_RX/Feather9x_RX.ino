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
#include <SD.h>
#include <TinyGPS.h>

bool writeLog(char* type, uint8_t* data);

#define RFM95_RST 2  // 
#define RFM95_CS  3  // 
#define RFM95_INT 0  // 

#define SD_CS 6
#define GPS_TX 5
#define GPS_RX 4

#define TX_LED      A5
#define RX_LED      A6
// Change to 434.0 or other frequency, must match RX's freq!
#define RF95_FREQ 915.0

#define LOG_FILENAME "log.txt"

// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);

// instantiate servo object
Servo servo;

HardwareSerial Serial1(GPS_RX, GPS_TX);
TinyGPS gps;
File logFile;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(RFM95_RST, OUTPUT);
  pinMode(TX_LED, OUTPUT);
  pinMode(RX_LED, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);

  Serial.begin(115200);
  while (!Serial) delay(1);
  delay(100);

 /* Start GPS Software Serial */ /* STM32 Use Serial1 port */
  Serial1.begin(9600);
  /* Init SD Card */
  Serial.print("Initializing SD card...");
  // see if the card is present and can be initialized:
  if (!SD.begin(SD_CS)) {
    Serial.println("Card failed, or not present");
    // don't do anything more:
    while (1)
      ;
  }
  Serial.println("Card initialized.");

  logFile = SD.open("log.txt", FILE_WRITE);
  if (logFile) {
    logFile.println("LOGGING FORMAT");
    logFile.println("Log Type,RSSI(dBm),SNR(db),Month/Day Hour:Minute:Second.Hundredths,Lat,Lon,Alt,Speed(km),data");
    //Also log the LOG formats
    logFile.close();
  } else {
    /* Unable to open file */
    Serial.println("Cannot open log.txt");
    while(1);
  }

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
}

void loop() {
  Serial.println("");
  for (unsigned long start = millis(); millis() - start < 1000;) {
    while (Serial1.available()) {
      char c = Serial1.read();
      // Serial.write(c);  // uncomment this line if you want to see the GPS data flowing
      gps.encode(c);
      // if (gps.encode(c)) {
        // Serial.println("GPS data successfully parsed!");
      // }
    }
  }

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
      Serial.print("\tRSSI: ");
      Serial.println(rf95.lastRssi(), DEC);
      Serial.print("\tSNR: ");
      Serial.println(rf95.lastSNR(), DEC);
      delay(50);
      digitalWrite(RX_LED, LOW);
      
      //LOG
      writeLog("RECV", (uint8_t*)buf, rf95.lastRssi(), rf95.lastSNR());
      
      // Send a reply
      uint8_t data[12] = "ACK #      ";
      memcpy(data+5, buf+9, 5);
      digitalWrite(TX_LED, HIGH);
      rf95.send(data, 12);
      rf95.waitPacketSent();
      Serial.println("Sent a reply");
      
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


bool writeLog(char* type, uint8_t* data, short rssi, int snr) {
  float flat, flon, falt, fspeed;
  gps.f_get_position(&flat, &flon);
  falt = gps.f_altitude();
  fspeed = gps.f_speed_kmph();
  int year;
  byte month, day, hour, minute, second, hundredths;
  gps.crack_datetime(&year, &month, &day, &hour, &minute, &second, &hundredths);
  // Serial.println(flat, 6);
  // Serial.println(flon, 6);
  // Serial.println(falt, 6);
  // Serial.print(hour);
  // Serial.print(":");
  // Serial.print(minute);
  // Serial.print(":");
  // Serial.println(second);
  char log_str[256];
  sprintf(log_str, "%s,%hi,%d,%02d/%02d %02d:%02d:%02d.%02d,%11.6f,%11.6f,%7.2f,%6.2f,%s",
          type, rssi, snr, month, day, hour, minute, second, hundredths, flat, flon, falt, fspeed, data);
  Serial.print("Logged: ");
  Serial.println(log_str);
  logFile = SD.open(LOG_FILENAME, FILE_WRITE);
  if (logFile) {
    logFile.println(log_str);
    logFile.close();
  } else {
    /* Unable to open file */
    return false;
  }
  return true;
}