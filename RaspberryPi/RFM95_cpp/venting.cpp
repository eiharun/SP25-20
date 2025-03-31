

#include <bcm2835.h>
#include <stdio.h>
#include <signal.h>
#include <unistd.h>
#include <iostream>

#include <RH_RF95.h>

#define RF_CS_PIN  26 
#define RF_IRQ_PIN 5 
#define RF_RST_PIN 19 
#define RF_FREQUENCY  915.00

RH_RF95 rf95(RF_CS_PIN, RF_IRQ_PIN);

volatile sig_atomic_t force_exit = false;

void sig_handler(int sig)
{
  printf("\n%s Break received, exiting!\n", __BASEFILE__);
  force_exit=true;
}

int main (int argc, const char* argv[] ){
    static unsigned long last_millis;
    static unsigned long led_blink = 0;
    
    signal(SIGINT, sig_handler);
    printf( "%s\n", __BASEFILE__);

    if (!bcm2835_init()) {
        fprintf( stderr, "%s bcm2835_init() Failed\n\n", __BASEFILE__ );
        return 1;
    }
    printf( "RF95 CS=GPIO%d", RF_CS_PIN);
    printf( ", IRQ=GPIO%d", RF_IRQ_PIN );
    // IRQ Pin input/pull down 
    pinMode(RF_IRQ_PIN, INPUT);
    bcm2835_gpio_set_pud(RF_IRQ_PIN, BCM2835_GPIO_PUD_DOWN);
    printf( ", RST=GPIO%d", RF_RST_PIN );
    // Pulse a reset on module
    pinMode(RF_RST_PIN, OUTPUT);
    digitalWrite(RF_RST_PIN, LOW );
    bcm2835_delay(150);
    digitalWrite(RF_RST_PIN, HIGH );
    bcm2835_delay(100);
    if (!rf95.init()) {
        fprintf( stderr, "\nRF95 module init failed, Please verify wiring/module\n" );
    } 
    else {
        printf( "\nRF95 module seen OK!\r\n");
    }

    rf95.available();
    // Now we can enable Rising edge detection
    bcm2835_gpio_ren(RF_IRQ_PIN);

    rf95.setTxPower(23, false); 
    rf95.setFrequency( RF_FREQUENCY );

    while (!force_exit) {
        std::cout << "Hello\n";
        bcm2835_delay(1000);

    }

}