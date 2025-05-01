#define LOGGING //COMMENT TO DISABLE LOGGING AND DEPENDENCIES (if you don't have GPS or SD card connected)
// #define LED //COMMENT TO DISABLE LEDS 

#include "Balloon.h"

void setup() {
  SystemClock_Config(); 
  pinMode(RFM95_RST, OUTPUT);
  pinMode(STATUS_LED, OUTPUT);
  #ifdef LED
  pinMode(RX_LED, OUTPUT);
  #endif
  digitalWrite(RFM95_RST, HIGH);
  digitalWrite(STATUS_LED, HIGH);

  /* Attach Servo Motor */
  motor.attach(SERVO_PIN, 500, 2400);
  if (!motor.attached()) {
  Serial.print("Servo motor not connected");
  }
  Serial.print("Servo motor connected");
  motor.write(SERVO_ANGLE_CLOSED);/* Starting Angle */

  /* Start Serial Output */
  Serial.begin(115200);
  while (!Serial) delay(1);
  delay(100);

  /* Start GPS Software Serial */ /* STM32 Use Serial1 port */
#ifdef LOGGING
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
    logFile.println("LOGGING START");
    logFile.close();
  } else {
    /* Unable to open file */
    Serial.println("Cannot open log.txt");
    while(1);
  }
#endif

  Serial.println("LoRa RX Test!");

  // manual reset
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);

  /* Init RFM95 */
  while (!rf95.init()) {
    Serial.println("LoRa radio init failed");
    while (1)
      ;
  }
  Serial.println("LoRa radio init OK!");

  if (!rf95.setFrequency(RF95_FREQ)) {
    Serial.println("setFrequency failed");
    while (1)
      ;
  }
  Serial.print("Set Freq to: ");
  Serial.println(RF95_FREQ);

  rf95.setTxPower(23, false);
  rf95.setSpreadingFactor(12);

  // PRINT REGISTERS FOR DEBUGGING
  // if (!rf95.printRegisters()) {
  //   Serial.println("printRegisters failed");
  //   while (1)
  //     ;
  // }
  
  current_state = AWAIT; 
  digitalWrite(STATUS_LED, LOW);
}

/* ---------------------LOOP-------------------- */
/* --------------------------------------------- */

uint8_t recv_buf[RH_RF95_MAX_MESSAGE_LEN];
uint8_t recv_buf_len = RH_RF95_MAX_MESSAGE_LEN;
int expected_seq=0;
int seq = 0;

void loop() {
#ifdef LOGGING
  /* Gather Data from GPS */
  Serial.println("");
  for (unsigned long start = millis(); millis() - start < 1000;) {
    while (Serial1.available()) {
      char c = Serial1.read();
      // Serial.write(c);  // uncomment this line if you want to see the GPS data flowing
      gps.encode(c);
    }
  }
#endif

  Serial.println("");
  switch (current_state) {
    case AWAIT: {
      /* Wait 'AWAIT_TIMEOUT' ms for reply
       * If no reply, loop around and wait again
       * If reply, change state to RECV
       */
      Serial.println("AWAIT STATE");
      if (rf95.waitAvailableTimeout(AWAIT_TIMEOUT)) {
        if (rf95.recv(recv_buf, &recv_buf_len)) {
          /* Extract the data segment from the recieved buffer */
          /* The modified radiohead recieve function puts the 
           * entire packet in the buffer, including the header 
           * so we have to extract the data segment from the buffer
           */
          uint8_t data[RH_RF95_MAX_MESSAGE_LEN-4];//-4 for the header
          uint8_t data_len;
          rf95.extractData(recv_buf, data, &data_len);
          memset(recv_buf, 0, recv_buf_len);
          memcpy(recv_buf, data, data_len);
          /* Set recieved buffer to data segment for reusability
           * recv_buf will not be used anywhere before first being overwritten by data */
          current_state = RECV;
        } else {
          /* Failed to recv (err) */
        }
      }
      break;
    }

    case RECV: {
      /* Process packet, send ACK
       * Change state to back to AWAIT 
       */
      Serial.println("RECV STATE");
      uint8_t got_seq = rf95.headerSeq();
      uint8_t cmd = rf95.headerCMD();
      uint8_t len = rf95.headerLen();
      Serial.print("Got Seq:");
      Serial.println(got_seq);
      Serial.print("Got cmd:");
      Serial.println(cmd);
      #ifdef LED
      digitalWrite(RX_LED, HIGH);
      #endif
      recv_t recv_pkt = {rf95.headerSeq(), rf95.headerAck(), rf95.headerCMD(), rf95.headerLen(), recv_buf, rf95.lastRssi(), rf95.lastSNR()};
#ifdef LOGGING
      /* LOG-TYPE,RSSI,SNR,Time,GPS-Coords,,,RecievedPacket */
      writeLog("RECV", recv_pkt);
#endif
      /* Reset/Resyncronize expected seq# */
      if(got_seq == 0)
        expected_seq = 0;
      /* Only takes action if it recieves the seq# is expects
       * Otherwise it will just send the packet back as an ack
       * This is assuming a duplicated packet was recieved by the GS 
       * meaning the first ack never got there
      */
      if(expected_seq == got_seq){
        /* If the motor is busy and the cmd is not (cutdown or close)
         * send BUSY in the ack. Otherwise, execute the command and send ack
        */
        if(MotorBusy && cmd != CUTDOWN && cmd != CLOSE /*&& cmd != ...*/){
          /* If cmd is cutdown or close bypass the busy flag because we 
           * don't care that the motor is busy, we want to close it, or cutdown the balloon
          */
          Serial.println("Sent ack-BUSY");
          cmd = BUSY;
        }
        else{
          Serial.println("Sent ack");
          interpret_command(recv_buf);
        }
        expected_seq=(expected_seq+1)%256;
        if(expected_seq==0){
          expected_seq=1;
        } 
      }
      //do nothing
      else{
        Serial.println("Sent Ack, Duplicated packet");
      }
      /* Send ACK */
      rf95.setHeaders(seq, got_seq, cmd, 0);
      rf95.send(NULL, 0);
      seq=(seq+1)%256;
      if(seq==0){
        seq=1;
      } 

      current_state = AWAIT;
      #ifdef LED
      digitalWrite(RX_LED, LOW);
      #endif
      break;
    }
    default:
      /* Should never get here */
      break;
  }
}

/* --------------------------------------------- */
/* -------------------END LOOP------------------ */

#ifdef LOGGING
/* Write Log to SD card */
bool writeLog(char* type, recv_t recv_pkt) {
  float flat, flon, falt, fspeed;
  gps.f_get_position(&flat, &flon);
  falt = gps.f_altitude();
  fspeed = gps.f_speed_kmph();
  int year;
  byte month, day, hour, minute, second, hundredths;
  gps.crack_datetime(&year, &month, &day, &hour, &minute, &second, &hundredths);
  char log_str[256];
  sprintf(log_str, "%s,%hi,%d,%02d/%02d %02d:%02d:%02d.%02d,%11.6f,%11.6f,%7.2f,%6.2f,%d:%d:%d:%d:%s",
          type, recv_pkt.rssi, recv_pkt.snr, month, day, hour, minute, second, hundredths, flat, flon, falt, fspeed, 
          recv_pkt.seq, recv_pkt.ack, recv_pkt.cmd, recv_pkt.len, recv_pkt.data);
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
#endif

void interpret_command(uint8_t* recv_buf){
  uint8_t cmd = rf95.headerCMD();
  uint8_t length = rf95.headerLen();
  if (cmd>0 && cmd<=11){
    Serial.print("No payload data: ");
    execute_command_0(cmd);
  }
  else if (cmd>11 && cmd<=193){
    uint8_t offset=0;
    if (length > 8){
      Serial.print("Truncating");
      Serial.println(length);
      offset = length-8;
      length = 8; //Cap length to 8
      /* Only read lower 8 bytes */
    }
    Serial.println("Binary Encoded data: ");
    uint64_t decimal=0;
    /* Decodes big endian decimal */
    for (size_t i = offset; i < length;i++){
      decimal = (decimal<<8) | recv_buf[i];
    }
    //Execute
    execute_command_1(cmd, decimal);
  }
  //else if (cmd range){  decode and do something } // Use to expand the command set
  else{
    Serial.print("Undefined Command Range");
    Serial.println(cmd);
  }

}

/* Closes motor and stops and resets hardware timer */
void resetMotor(){
  motor.write(SERVO_ANGLE_CLOSED);
  MotorBusy = false;
  Serial.println("Timer ended");
  motorTimer->pause();
  motorTimer->setCount(0);
}

/* Execute Commands with no payload */
void execute_command_0(uint8_t cmd){
  switch(cmd){
    case cIDLE: {
      Serial.println("Idle, do nothing");
      break;
    }
    case CUTDOWN: {
      Serial.println("Cutdown");
      break;
    }
    case CLOSE: {
      if(MotorBusy){
        resetMotor();
      }
      break;
    }
    default: {
      Serial.print("Unknown command");
      Serial.println(cmd);
      break;
    }
  }
}

/* Execute commands with binary number payload */
void execute_command_1(uint8_t cmd, uint64_t num){
  switch(cmd){
    case cIDLE: {
      Serial.println("Idle, do nothing");
      break;
    }
    case CUTDOWN: {
      Serial.println("Cutdown");
      break;
    }
    case CLOSE: {
      if(MotorBusy){
        resetMotor();
      }
      break;
    }
    case OPENs: {
      Serial.print("Open (s): ");
      Serial.println(num);
      motor.write(SERVO_ANGLE_OPEN);      
      motorTimer->setPrescaleFactor(65535);
      motorTimer->attachInterrupt(resetMotor);
      uint32_t arr = (uint32_t)num * 1221;
      motorTimer->setOverflow(arr);
      
      motorTimer->setCount(0);
      motorTimer->resume();
      Serial.println("Timer started");
      MotorBusy = true;
      break;
    }
    default: {
      Serial.print("Unknown command");
      Serial.println(cmd);
      break;
    }
  }
}

/* Add other command types here */
/* Use this as a template - Make sure to add new commands the the commands_t enum in Balloon.h
 * and add the command range in interpret_command() to call this function 
 
void execute_command_x(uint8_t cmd, data_type data_value){
  switch(cmd){
    case A COMMAND: {
      Serial.println("Idle, do nothing");
      break;
    }
    case ANOTHER COMMAND: {
      Serial.println("Cutdown");
      break;
    }
    case YET ANOTHER COMMAND: {
      if(MotorBusy){
        resetMotor();
      }
      break;
    }
    default: {
      Serial.print("Unknown command");
      Serial.println(cmd);
      break;
    }
  }
}
*/