#define LOGGING //COMMENT TO DISABLE LOGGING AND DEPENDENCIES (if you don't have GPS or SD card connected)

#include "Balloon.h"

void setupTimer2_1Hz() {
  // Enable TIM2 clock
  RCC->AHB1ENR |= RCC_APB1ENR1_TIM2EN;
  TIM2->CNT = 0;
  TIM2->PSC = 64000 - 1;   // Prescaler: 64 MHz / 64k = 1 kHz
  TIM2->ARR = 300000 - 1;    // Auto-reload: 300,000 ms = 5 min
  TIM2->DIER |= TIM_DIER_UIE;   // Enable update interrupt
  TIM2->CR1 &= ~TIM_CR1_CEN;     // Disable counter

  NVIC_EnableIRQ(TIM2_IRQn);    // Enable interrupt in NVIC
}

void pauseTimer2() {
  TIM2->CR1 &= ~TIM_CR1_CEN;     // Disable counter
  TIM2->DIER &= ~TIM_DIER_UIE;   // Disable update interrupt
}

void resetTimer2() {
  TIM2->CNT = 0;
  TIM2->DIER |= TIM_DIER_UIE;    // Enable update interrupt
  TIM2->CR1 |= TIM_CR1_CEN;      // Enable counter
}

void setup() {
  pinMode(RFM95_RST, OUTPUT);
  pinMode(TX_LED, OUTPUT);
  pinMode(RX_LED, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);

  /* Attach Servo Motor */
  motor.attach(SERVO_PIN, 500, 2400);
  if (!motor.attached()) {
  Serial.print("Servo motor not connected");
  }
  Serial.print("Servo motor connected");
  motor.write(0);/* Starting Angle */

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
  // rf95.setSignalBandwidth(12500);

  if (!rf95.printRegisters()) {
    Serial.println("printRegisters failed");
    while (1)
      ;
  }

  // interrupt setup
  pinMode(RFM95_INT, INPUT); // needed for interrupt detection
  

  // setupTimer2_1Hz();
  // pauseTimer2();

  current_state = IDLE;
}

uint8_t recv_buf[RH_RF95_MAX_MESSAGE_LEN];
uint8_t recv_buf_len = sizeof(recv_buf);

const int interval = 5 * 60 * 1000; // 5 minutes between idle packets, can change
unsigned long lastWakeTime = 0;
unsigned long lastReceivedTime = 0;

// from STM32 forum
void enterSleepMode(){
  resetTimer2();
  HAL_SuspendTick();
  HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
}

void TIM2_IRQHandler(void) {
  if (TIM2->SR & TIM_SR_UIF) {         // Check update interrupt flag
    TIM2->SR &= ~TIM_SR_UIF;           // Clear the flag 
    TIM2->CNT = 0;

    HAL_ResumeTick();
    Serial.println("timer 2 expired\n");
  }
}

/* ---------------------LOOP-------------------- */
/* --------------------------------------------- */
int seq=0;
void loop() {
  unsigned long currentMillis = millis();
#ifdef LOGGING
  /* Gather Data from GPS */
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
#endif

  Serial.println("");
  switch (current_state) {
    case IDLE: {

      /* Send IDLE packet, change state to AWAIT */
      Serial.println("IDLE STATE");
      /* IDLE HEADER - Seq#, Ack#(N/A), CMD-0x01, len=0 */
      rf95.setHeaders(seq,0,1,0);
      rf95.send(NULL, 0); /* Do not send any data. Only Send header with IDLE cmd */
      seq=(seq+1)%256;
      // rf95.send((uint8_t*)radiopacket, sizeof(radiopacket));
      // Serial.println("Sleep mode");
      // // start timer to break sleep, only timer breaks sleep mode
      // Serial.println("entering sleep mode\n");
      // enterSleepMode();
      // pauseTimer2();
      // packetReceived = false;
      // Serial.println("Exiting sleep mode\n");
#ifdef LOGGING
      writeLog("IDLE", (uint8_t*)"Idle Sent");
#endif
      current_state = AWAIT;
      break;
    }
    case AWAIT: {
      /* Wait 'AWAIT_TIMEOUT' ms for reply
       * If no reply, change state to IDLE, sleep for 'y' seconds/minutes
       * If reply, change state to RECV
       */

      // unsigned long startTime = millis();
      // bool received = false;

      // while (millis() - startTime >= AWAIT_TIMEOUT) {
      //   if (rf95.available()){
      //     received = true;
      //     break;
      //   }
      // }
      
      // if (received){
      //   current_state = RECV;
      //   break;
      // }

      // else{
      //   current_state = IDLE;
      //   break;
      // }

      Serial.println("AWAIT STATE");
      if (rf95.waitAvailableTimeout(AWAIT_TIMEOUT)) {
        memset(recv_buf, 0, recv_buf_len);
        if (rf95.recv(recv_buf, &recv_buf_len)) {
          current_state = RECV;
        } else {
          /* Failed to recv (err) */
        }
      } else {
        current_state = IDLE;
        /* GO TO SLEEP */ /* TODO:
                           * In sleep mode set up interrupt when any packet is recieved
                           * to wake up and change state to RECV
                           */
        Serial.println("SLEEP");
        delay(1000);  //artificially sleep
      }
      break;
    }

    case RECV: {
      /* Process packet, send ACK (possibly with telemetry)
       * Change state to AWAKE 
       */
      Serial.println("RECV STATE");
      /* Do something with recv_buf */
      uint8_t ack = rf95.headerSeq() + 1;
      uint8_t cmd = rf95.headerCMD();

      digitalWrite(RX_LED, HIGH);
      Serial.print("Got: ");
      Serial.println((char*)recv_buf);
      delay(400);
      digitalWrite(RX_LED, LOW);
#ifdef LOGGING
      /* LOG-TYPE,Time,GPS-Coords,,,RecievedPacket */
      writeLog("RECV", recv_buf);
#endif

      interpret_command(recv_buf);
      /* Send ACK */
      rf95.setHeaders(seq, ack, cmd, 0);
      rf95.send(NULL, 0);
      seq=(seq+1)%256;
      // memset(recv_buf, 0, recv_buf_len); /* Clear buffer */
      current_state = AWAKE;
      lastReceivedTime=millis();
      break;
    }
    case AWAKE: {
      /* If inactivity (nothing recieved) after z minutes, go back to IDLE state 
       *    (for now reset to go back to idle)
       * Continuous recieving mode
       * If something is recieved, change state to RECV
       */
      Serial.println("AWAKE STATE");

      if (rf95.available()) {
        lastReceivedTime = millis();
        memset(recv_buf, 0, recv_buf_len);
        if (rf95.recv(recv_buf, &recv_buf_len)) {
          current_state = RECV;
        } else {
          /* Failed to recv (err) */
        }
      }

      else if (millis() - lastReceivedTime > INACTIVITY_TIMEOUT) {
        Serial.println("Awake Timeout");
        current_state = IDLE;
      }
      break;
    default:
      /* Should never get here */
      break;
    }
  }
}

#ifdef LOGGING
bool writeLog(char* type, uint8_t* data) {
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
  sprintf(log_str, "%s,%02d/%02d %02d:%02d:%02d.%02d,%11.6f,%11.6f,%7.2f,%6.2f,%s",
          type, month, day, hour, minute, second, hundredths, flat, flon, falt, fspeed, data);
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
    Serial.println(recv_buf[0]);
    execute_command_0(cmd);
  }
  else if (cmd>11 && cmd<=193){
    Serial.print("BCD Encoded data: ");
    int decimal=0;
    /* Decodes big endian decimal */
    for (size_t i = 0; i< length;i++){
      decimal = (decimal<<8) | recv_buf[i];
    }
    //Execute
    execute_command_1(cmd, decimal);
  }
  // else if (cmd range){ decode and do something } // Use to expand the command set
  else{
    Serial.print("Undefined Command Range");
    Serial.println(cmd);
  }
}

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
    default: {
      Serial.print("Unknown command");
      Serial.println(cmd);
      break;
    }
  }
}

void execute_command_1(uint8_t cmd, uint8_t num){
  switch(cmd){
    case OPENs: {
      Serial.print("Open (s): ");
      Serial.println(num);
      break;
    }
    case OPENm: {
      Serial.print("Open (m): ");
      Serial.println(num);
      break;
    }
    default: {
      Serial.print("Unknown command");
      Serial.println(cmd);
      break;
    }
  }
}
