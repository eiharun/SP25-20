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

#define RF95_FREQ 915.0
#define AWAIT_TIMEOUT 15000 /* Time in MS to wait after IDLE packet was sent to recieve a reply. MAX is 65535 */

enum State {IDLE, AWAIT, RECV, AWAKE};

State current_state;
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
  rf95.setSpreadingFactor(12);
  // rf95.setSignalBandwidth(12500);

  if (!rf95.printRegisters()) {
    Serial.println("printRegisters failed");
    while (1);
  }
  current_state = IDLE;
}
uint8_t recv_buf[RH_RF95_MAX_MESSAGE_LEN];
uint8_t recv_buf_len = sizeof(recv_buf);

void loop() {
  switch(current_state){
    case IDLE:
      /* Send IDLE packet, change state to AWAIT */
      Serial.println("IDLE STATE");
      strcpy(radiopacket, "IDLE");
      radiopacket[4]=0;
      rf95.send(radiopacket, sizeof(radiopacket));
      current_state = AWAIT;
      break;
    case AWAIT:
      /* Wait 'AWAIT_TIMEOUT' ms for reply
       * If no reply, change state to IDLE, sleep for 'y' seconds/minutes
       * If reply, change state to RECV
       */
      Serial.println("AWAIT STATE");
      if (rf95.waitAvailableTimeout(AWAIT_TIMEOUT)) {
        if (rf95.recv(recv_buf, &recv_buf_len)) {
          current_state = RECV;
        }
        else{
          /* Failed to recv (err) */
        }
      }
      else{
        current_state = IDLE;
        /* GO TO SLEEP */ /* TODO:
                           * In sleep mode set up interrupt when any packet is recieved
                           * to wake up and change state to RECV
                           */
        Serial.println("SLEEP"); 
        delay(5000); //artificially sleep
      }
      break;
    case RECV:
      /* Process packet, send ACK (possibly with telemetry)
       * Change state to AWAKE 
       */
      Serial.println("RECV STATE");
      /* Do something with recv_buf */
      digitalWrite(RX_LED, HIGH);
      Serial.print("Got: "); Serial.println((char*)recv_buf);
      delay(400);
      digitalWrite(RX_LED, LOW);

      memset(radiopacket, 0, sizeof(radiopacket));
      strcpy(radiopacket, "ACK + TELEMETRY");
      rf95.send(radiopacket, sizeof(radiopacket));
      memset(recv_buf, 0, recv_buf_len); /* Clear buffer */
      current_state = AWAKE;
      break;
    case AWAKE:
      /* If inactivity (nothing recieved) after z minutes, go back to IDLE state 
       *    (for now reset to go back to idle)
       * Continuous recieving mode
       * If something is recieved, change state to RECV
       */
      if(rf95.available()){
        Serial.println("AWAKE STATE");
        if (rf95.recv(recv_buf, &recv_buf_len)) {
          current_state = RECV;
        }
        else{
          /* Failed to recv (err) */
        }
      }
      break;
    default:
      /* Should never get here */
      break;
  }

}
