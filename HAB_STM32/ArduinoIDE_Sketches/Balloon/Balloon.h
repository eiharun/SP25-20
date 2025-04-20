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

#define RH_RF95_MAX_MESSAGE_LEN RH_RF95_MAX_PAYLOAD_LEN

enum commands_t {
  cIDLE=1, CUTDOWN=2, CLOSE=3, OPENs=64, OPENm=65
};

enum state_t { LOWPOWER,
               AWAIT,
               RECV,
               AWAKE };
state_t current_state;

struct recv_t {
  uint8_t seq;
  uint8_t ack;
  uint8_t cmd;
  uint8_t len;
  uint8_t* data;
  short rssi;
  int snr;
};

// Singleton instance of the radio driver
RH_RF95_CH rf95(RFM95_CS, RFM95_INT);

#ifdef LOGGING
HardwareSerial Serial1(GPS_RX, GPS_TX);
TinyGPS gps;
File logFile;
#endif

Servo motor;

HardwareTimer* motorTimer = new HardwareTimer(TIM2);  
uint32_t timFreq = motorTimer->getTimerClkFreq();

bool MotorBusy;

#ifdef LOGGING
bool writeLog(char* type, recv_t recv_pkt);
#endif
void interpret_command(uint8_t* recv_buf);
void execute_command_0(uint8_t cmd);
void execute_command_1(uint8_t cmd, uint64_t num);

