from enum import Enum

class Commands(Enum):
    DEFAULT=0       # Default. Not in use
    #############
    IDLE=1      # ONLY USED BY THE BALLOON
    CUTDOWN=2   # Cutdown the balloon
    CLOSE=3     # Close the vent
    #up to 11
    OPEN=64    # Open for x seconds, then close
    #up to 193
    #commands with tbd data encoding schemes
    # ...
    ##############
    BUSY=255  # Flag sent from balloon to indicate that the vent is open
    #up to 255

# Structure of the commands Enum:
#0: Reserved DEFAULT
#1-63: Reserved for commands with no data payload (len=0)
#64-191: Reserved for commands with binary number data payloads (with MAX len=8) This is plenty as it can represent 5849424173.55072 centuries duration
#192-254: Reserved for commands with TBD encoded data payloads
# Subject to change as more commands are added
#255: Reserved for BUSY flag - may optionally have payload to indicate which resource is busy if needed
