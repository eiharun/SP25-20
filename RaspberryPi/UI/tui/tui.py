from rfm95api import *
import logging
import cmd

logger = logging.getLogger(__name__)

class TUI:
    """
    Texual User Interface allows more contol over application in comparison to the GUI.
    It also allows ease of testing.
    """
    def __init__(self):
        constructor = RFM95Wrapper()
        self.rfm95 = constructor.construct()
        logger.debug("RFM95 Constructed")

    def run(self):
        try:
            logger.debug("Starting TUI")
            print("Starting TUI")
            tui_command = TUICommand(self.rfm95)
            tui_command.cmdloop()
        except KeyboardInterrupt:
            print()
            logger.debug("Exiting Ground Station TUI")
            print("Exiting Ground Station TUI")
            exit(0)
            
class TUICommand(cmd.Cmd):
    """
    Command line interface for the RFM95 wrapper.
    """
    prompt = "RFM95> "
    
    def __init__(self, rfm95):
        super().__init__()
        self.rfm95 = rfm95
        self.intro = "Welcome to the RFM95 CLI. Type help or ? to list commands.\n"
        self.intro += "Type 'exit' to exit the CLI.\n"
        self.intro += "Type 'help <command>' for help on a specific command.\n"
        self.intro += "Type 'clear' to clear the screen.\n"
        
        self.send_on_idle = True
        self._idle_status = False
        self.seq = 0
        
        
    #----------------COMMANDS SET-------------------------#
    def do_open(self, arg):
        """Open the vent for 'x' (sec/min)
    Usage: OPEN x [s/m]
    \t x - number of seconds
    \t [s/m] - specify s or m for seconds or minutes
    To open the vent for 5 minutes
    \tOPEN 5 m 
    To open the vent for 10 seconds
    \tOPEN 10 s
    """
        assert len(arg.split(' ')) == 2
        duration = int(arg.split(' ')[0])
        unit = arg.split(' ')[1].lower()
        assert unit == 's' or unit == 'm'
        if not self.verify_send_on_idle():
            return
        print("Waiting for IDLE (balloon to be in range)")
        print(f"Opening vent for {duration} {'seconds' if unit == 's' else 'minutes'}")
        cmd = 0
        if unit == 's':
            cmd = Commands.OPENs.value
        elif unit == 'm':
            cmd = Commands.OPENm.value
        assert cmd != 0
        num_bytes = self.byte_length(duration)
        payload = duration.to_bytes(num_bytes, byteorder='big')
        logger.debug(f"Verification: {duration}:{payload}:{num_bytes}:{int.from_bytes(payload,'big')}")
        #TODO: Wait for idle
        self.rfm95.send(payload, seq=self.seq, ack=0, CMD=cmd, length=num_bytes)
        self.seq = (self.seq+1)%256
        recv = self.rfm95.receive(timeout=5)
        if recv is None:
            print("No Ack recieved. Verify gps data before resending")
        else:
            seq,ack,cmd,length,data = self.rfm95.extractHeaders(recv)
            # Expected to recieve an ACK with ack# = prev seq#+1, cmd=0, length=0, and data=cmd
            print(f"Recieved Headers: {seq} {ack} {cmd} {length}")
            print(f"Recieved Ack: {data}")
            print(f"\tSignal Strength: {self.rfm95.last_rssi}")
            print(f"\tSNR: {self.rfm95.last_snr}")
        
    def do_cutdown(self):
        """"Cutdown the balloon"""
        answer = input("Are you sure you want to cutdown the balloon? y/n:")
        if answer.lower() == 'y':
            #send cutdown
            pass
        else:
            print("Ok, returning")
            return
        
    #----------------MISC---------------------------------#    
        
    def do_disable_idle(self):
        """ONLY USE IF YOU KNOW WHAT YOU'RE DOING \nWill disable sending on recieved IDLE. \n Will not wait to recieve an IDLE from the balloon before sending"""
        self.send_on_idle = False
        
    def do_enable_idle(self):
        """Will enable sending on recieved IDLE. \nWill wait to recieve an IDLE from the balloon before sending"""
        self.send_on_idle = True
    
    #----------------OTHER UI COMMANDS--------------------#    
        
    def default(self, line):
        print(f"Unknown command: {line}")
        
    def emptyline(self):
        return
        
    def do_exit(self, arg):
         """Exits the shell."""
         return True
     
    def do_help(self, arg):
        """Displays the help screen"""
        return super().do_help(arg)
    
    def do_clear(self, arg):
        """Clears the screen."""
        print("\033[H\033[J", end="")
        print(self.intro)
        return False
    
    #----------------HELPERS------------------------------#    
    
    def verify_send_on_idle(self):
        if not self.send_on_idle:
            print("WARNING: This command will not wait for an IDLE packet from the balloon. It will send immediately")
            answer = input("Are you sure? y/n: ")
            if answer.lower() == 'y':
                return True
            elif answer.lower() == 'n':
                print("Aborting...")
                return False
            else:
                print("Incorrect input")
                return False
        else:
            return True
        
    def byte_length(self,i):
        return (i.bit_length() + 7) // 8
