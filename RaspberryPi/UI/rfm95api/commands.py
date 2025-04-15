from enum import Enum

class Commands(Enum):
    DEFAULT=0       # Default. Not in use
    #############
    IDLE=1      # ONLY USED BY THE BALLOON
    CUTDOWN=2   # Cutdown the balloon
    #up to 11
    OPENs=64    # Open for x seconds, then close
    OPENm=65    # Open for x minutes, then close
    #up to 193
    #commands with tbd data encoding schemes
    TEST=194    # Test command
    #up to 255
    
# Structure of the commands Enum:
#0: Reserved DEFAULT
#1-63: Reserved for commands with no data payload (len=0)
#64-191: Reserved for commands with binary number data payloads (with MAX len=8) This is plenty as it can represent 5849424173.55072 centuries duration
#192-255: Reserved for commands with TBD encoded data payloads
# Subject to change as more commands are added

