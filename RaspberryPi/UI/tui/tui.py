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
            f = open("idle.log", 'w')
            f.close()
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
        self.cmd = Commands.DEFAULT.value
        
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
        assert duration < 2**(8*8) #Max len is 8
        assert unit == 's' or unit == 'm'
        self.cmd = Commands.OPENs.value if unit == 's' else Commands.OPENm.value
        assert self.cmd != Commands.DEFAULT.value
        num_bytes, payload = self.byte_w_len(duration)
        self.rfm95.send(payload, seq=self.seq, ack=0, CMD=self.cmd, length=num_bytes)

        logger.debug(f"Verification: {duration}:{payload}:{num_bytes}:{int.from_bytes(payload,'big')}")
        print(f"Opening vent for {duration} {'seconds' if unit == 's' else 'minutes'}")
        print(f"Sent Headers: {self.seq} {self.cmd} {num_bytes}")

        self.seq = (self.seq+1)%256
        recv = self.rfm95.receive(timeout=5)

        if recv is None:
            print("No Ack recieved. Verify gps data before resending")
        else:
            seq,ack,cmd,length,data = self.rfm95.extractHeaders(recv)
            if cmd == 255:
                print("Balloon is busy. Motor is open. Send close command to close it")
            print(f"Recieved Headers: {seq} {ack} {cmd} {length} {data}")
            print(f"\tSignal Strength: {self.rfm95.last_rssi}")
            print(f"\tSNR: {self.rfm95.last_snr}")

    def do_cutdown(self, arg):
        """"Cutdown the balloon"""

        answer = input("Are you sure you want to cutdown the balloon? y/n:")
        if answer.lower() == 'y':
            print("Sending cutdown command")
            self.rfm95.send(b'\x00', seq=self.seq, ack=0, CMD=Commands.CUTDOWN.value, length=0)
            self.seq = (self.seq+1)%256
            recv = self.rfm95.receive(timeout=5)

            if recv is None:
                print("No Ack recieved. Verify gps data before resending")
            else:
                seq,ack,cmd,length,data = self.rfm95.extractHeaders(recv)
                if cmd == 255:
                    print("Motor is open. Now Opening indefinitely")
                print(f"Recieved Headers: {seq} {ack} {cmd} {length} {data}")
                print(f"\tSignal Strength: {self.rfm95.last_rssi}")
                print(f"\tSNR: {self.rfm95.last_snr}")
        else:
            print("Ok, returning")
            return
        
    def do_idle(self, arg):
        """Sends an IDLE command to the balloon 
        Usage: IDLE"""

        print("Sending idle command")
        self.rfm95.send(b'', seq=self.seq, ack=0, CMD=Commands.IDLE.value, length=0)
        self.seq = (self.seq+1)%256
        recv = self.rfm95.receive(timeout=5)
        if recv is None:
            print("No Ack recieved. Verify gps data before resending")
        else:
            seq,ack,cmd,length,data = self.rfm95.extractHeaders(recv)
            if cmd == 255:
                print("Balloon is busy. Motor is open. Send close command to close it")
            print(f"Recieved Headers: {seq} {ack} {cmd} {length} {data}")
            print(f"\tSignal Strength: {self.rfm95.last_rssi}")
            print(f"\tSNR: {self.rfm95.last_snr}")
    
    def do_close(self, arg):
        """"Closes the balloon vent"""
        
        answer = input("Are you sure you want to close the balloon? y/n:")
        if answer.lower() == 'y':
            print("Sending close command")
            self.rfm95.send(b'\x00', seq=self.seq, ack=0, CMD=Commands.CLOSE.value, length=0)
            self.seq = (self.seq+1)%256
            recv = self.rfm95.receive(timeout=5)

            if recv is None:
                print("No Ack recieved. Verify gps data before resending")
            else:
                seq,ack,cmd,length,data = self.rfm95.extractHeaders(recv)
                if cmd == 255:
                    print("Motor is open. Closing")
                print(f"Recieved Headers: {seq} {ack} {cmd} {length} {data}")
                print(f"\tSignal Strength: {self.rfm95.last_rssi}")
                print(f"\tSNR: {self.rfm95.last_snr}")
        else:
            print("Ok, returning")
            return
    #----------------MISC---------------------------------#    
        
    def preloop(self):
        """Initialization before the command loop starts."""
        print("Starting the CLI...")
        
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
    
    def byte_w_len(self, i:int):
        """
        Returns the number of bytes and the byte array of the given String.
        """
        assert isinstance(i, int), "Argument in byte_w_len() must be a string"
        num_bytes = (i.bit_length() + 7) // 8
        return num_bytes, i.to_bytes(num_bytes, byteorder='big')

