#include <SPI.h>
#include <RH_RF95_CH.h>
#include <Servo.h>
#include <Arduino.h>
#include <Wire.h>

#ifdef LOGGING
#include <SD.h>
#include <TinyGPS.h>
#define LOG_FILENAME "log.txt"
#endif 

#define RFM95_RST 2
#define RFM95_CS 3
#define RFM95_INT 0
#define TX_LED A5
#define RX_LED A6
#define SD_CS 6
#define SERVO_PIN 9
#define GPS_TX 5
#define GPS_RX 4

#define RF95_FREQ 915.0
#define AWAIT_TIMEOUT 5000  //15000 /* Time in MS to wait after IDLE packet was sent to recieve a reply. MAX is 65535 */
#define INACTIVITY_TIMEOUT 10000//300000

#define SERVO_ANGLE 100

enum commands_t {
  cIDLE=1, CUTDOWN=2, OPENs=64, OPENm=65
};

enum state_t { IDLE,
               AWAIT,
               RECV,
               AWAKE };
state_t current_state;

// Singleton instance of the radio driver
RH_RF95_CH rf95(RFM95_CS, RFM95_INT);

#ifdef LOGGING
HardwareSerial Serial1(GPS_RX, GPS_TX);
TinyGPS gps;
File logFile;
#endif

Servo motor;

#ifdef LOGGING
bool writeLog(uint8_t* data);
#endif
void interpret_command(uint8_t* recv_buf);
void execute_command_0(uint8_t cmd);
void execute_command_1(uint8_t cmd, uint8_t num);

