from rfm95api import *
import board
import digitalio
import logging
import cmd

logger = logging.getLogger(__name__)

class TUI:
    """
    Texual User Interface allows more contol over application in comparison to the GUI.
    It also allows ease of testing.
    """
    def __init__(self, 
                 SCK:DigitalInOut = board.SCK,
                 MOSI:DigitalInOut = board.MOSI, 
                 MISO:DigitalInOut = board.MISO,
                 CS:DigitalInOut = digitalio.DigitalInOut(board.D26),
                 RESET:DigitalInOut = digitalio.DigitalInOut(board.D19),
                 FREQ:float = 915.0):
        constructor = RFM95Wrapper(SCK, MOSI, MISO, CS, RESET, FREQ)
        rfm95 = constructor.construct()
        logger.debug("RFM95 Constructed")

    def run(self):
        try:
            #while loop
            pass
        except KeyboardInterrupt:
            logger.info("Exiting Ground Station TUI")
            print("Exiting Ground Station TUI")
            exit(0)
            