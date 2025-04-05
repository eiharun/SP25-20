from enum import Enum

class Commands(Enum):
    DEFAULT=0  # Reserved: Default, no action (no command is set)
    IDLE=1      #
    CUTDOWN=2   #
    #up to 11
    OPENs=64      # Open for x seconds, then close
    OPENm=64      # Open for x minutes, then close
    #up to 193
    #commands with tbd data encoding schemes
    TEST=194     # Test command
    #up to 255

# Structure of the commands Enum:
#0-63: Reserved for commands with no data payload
#64-191: Reserved for commands with BCD data payloads
#192-255: Reserved for commands with TBD encoded data payloads
# Subject to change as more commands are added

