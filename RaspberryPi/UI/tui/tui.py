from rfm95api import *
import logging
import cmd
from functools import wraps

logger = logging.getLogger(__name__)

def handle_assertion(func):
    """
    A decorator that handles assertion errors
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except AssertionError as e:
            print(e)
    return wrapper

class TUI:
    """
    Texual User Interface allows more contol over application in comparison to the GUI.
    It also allows ease of testing.
    """
    def __init__(self):
        constructor = RFM95Wrapper()
        self.rfm95 = constructor.construct()
        logger.info("RFM95 Constructed")

    def run(self):
        try:
            logger.info("Starting TUI")
            print("Starting TUI")
            tui_command = TUICommand(self.rfm95)
            tui_command.cmdloop()
        except KeyboardInterrupt:
            print()
            logger.info("Exiting Ground Station TUI")
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
        
        self.intro = "Welcome to the RFM95 CLI.\n\n"
        self.intro += "Type 'clear' to clear the screen.\n"
        self.intro += "Type 'help' or '?' a list of commands.\n"
        self.intro += "Type 'help <command>' for help on a specific command.\n"
        self.intro += "Type 'exit' to exit the CLI.\n"
        
        self.send_on_idle = True
        self._idle_status = False
        self.seq = 0
        self.cmd = Commands.DEFAULT.value
        self.RFMtimeout = 5
        
    #----------------COMMANDS SET-------------------------#
    @handle_assertion
    def do_open(self, arg):
        """Open the balloon vent for a given duration"""
        assert len(arg.split(' ')) == 2, "Invalid number of arguments. Requires at 2. Usage: open x [s/m]"
        assert arg.split(' ')[0].isdigit(), "Argument 'x' must be a number"
        duration = int(arg.split(' ')[0])
        assert duration > 0, "Duration must be greater than 0"
        unit = arg.split(' ')[1].lower()
        assert unit == 's' or unit == 'm', "Invalid unit. Must be 's' or 'm'"
        self.cmd = Commands.OPEN.value 
        if unit == 'm':
            duration = duration * 60 # Instead of having an OPENm command, we convert minutes to seconds as 4 bytes is enough to represent 50k days
        assert duration < 2**(4*8), "Duration is too long. Max duration is 2^32-1 seconds [4 bytes]"
        num_bytes, payload = self.byte_w_len(duration)
        self.rfm95.send(payload, seq=self.seq, ack=0, CMD=self.cmd, length=num_bytes)
        logger.debug(f"Verification: {duration}:{payload}:{num_bytes}:{int.from_bytes(payload,'big')}")
        logger.debug(f"Payload Verification: {duration}:{payload}:{num_bytes}:{int.from_bytes(payload,'big')}")
        print(f"Opening vent for {duration} {'seconds' if unit == 's' else 'minutes'}")
        logger.debug(f"Sent Headers: {self.seq} 0 {self.cmd} {num_bytes}: {payload}")
        logger.info(f"Opening vent for {duration} {'seconds' if unit == 's' else 'minutes'}")

        self.seq = (self.seq+1)%256
        recv = self.rfm95.receive(timeout=self.RFMtimeout)

        if recv is None:
            print("No Ack recieved. Verify gps data before resending")
            logger.debug("No Ack recieved. Verify gps data before resending")
        else:
            seq,ack,cmd,length,data = self.rfm95.extractHeaders(recv)
            if cmd == 255:
                print("Balloon is busy. Motor is open. Send close command to close it")
                logger.info("Balloon is busy. Motor is open. Send close command to close it")
            logger.debug(f"Recieved Headers: {seq} {ack} {cmd} {length} {data}")
            logger.debug(f"\tSignal Strength: {self.rfm95.last_rssi}")
            logger.debug(f"\tSNR: {self.rfm95.last_snr}")
            print("Received ACKNOWLEDGEMENT!")

    @handle_assertion
    def do_cutdown(self, arg):
        """"Cutdown the balloon"""
        assert len(arg) == 0, "cutdown takes no arguments"
        answer = input("Are you sure you want to cutdown the balloon? y/n:")
        if answer.lower() == 'y':
            print("Sending cutdown command")
            self.rfm95.send(b'\x00', seq=self.seq, ack=0, CMD=Commands.CUTDOWN.value, length=0)
            logger.debug(f"Sent Headers: {self.seq} 0 {self.cmd} 0")
            self.seq = (self.seq+1)%256
            recv = self.rfm95.receive(timeout=self.RFMtimeout)

            if recv is None:
                print("No Ack recieved. Verify gps data before resending")
                logger.info("No Ack recieved. Verify gps data before resending")
            else:
                seq,ack,cmd,length,data = self.rfm95.extractHeaders(recv)                
                logger.debug(f"Recieved Headers: {seq} {ack} {cmd} {length} {data}")
                logger.debug(f"\tSignal Strength: {self.rfm95.last_rssi}")
                logger.debug(f"\tSNR: {self.rfm95.last_snr}")
                print("Received ACKNOWLEDGEMENT!")            
        else:
            print("Ok, returning")
            return
        
    @handle_assertion
    def do_idle(self, arg):
        """Sends an IDLE command to the balloon 
        Usage: IDLE"""
        assert len(arg) == 0, "idle takes no arguments"
        print("Sending idle command")
        self.rfm95.send(b'', seq=self.seq, ack=0, CMD=Commands.IDLE.value, length=0)
        logger.debug(f"Sent Headers: {self.seq} 0 {self.cmd} 0")
        self.seq = (self.seq+1)%256
        recv = self.rfm95.receive(timeout=self.RFMtimeout)
        if recv is None:
            print("No Ack recieved")
            logger.info("No Ack recieved")
        else:
            seq,ack,cmd,length,data = self.rfm95.extractHeaders(recv)
            if cmd == 255:
                print("Balloon is busy. Motor is open. Send close command to close it")
                logger.info("Balloon is busy. Motor is open. Send close command to close it")
            logger.debug(f"Recieved Headers: {seq} {ack} {cmd} {length} {data}")
            logger.debug(f"\tSignal Strength: {self.rfm95.last_rssi}")
            logger.debug(f"\tSNR: {self.rfm95.last_snr}")
            print("Received ACKNOWLEDGEMENT!")            

    @handle_assertion
    def do_close(self, arg):
        """Closes the balloon vent""" 
        assert len(arg) == 0, "close takes no arguments"
        answer = input("Are you sure you want to close the balloon? y/n:")
        if answer.lower() == 'y':
            print("Sending close command")
            self.rfm95.send(b'\x00', seq=self.seq, ack=0, CMD=Commands.CLOSE.value, length=0)
            logger.debug(f"Sent Headers: {self.seq} 0 {self.cmd} 0")
            self.seq = (self.seq+1)%256
            recv = self.rfm95.receive(timeout=self.RFMtimeout)

            if recv is None:
                print("No Ack recieved. Feel free to resend")
                logger.debug("No Ack recieved. Feel free to resend")
            else:
                seq,ack,cmd,length,data = self.rfm95.extractHeaders(recv)
                logger.debug(f"Recieved Headers: {seq} {ack} {cmd} {length} {data}")
                logger.debug(f"\tSignal Strength: {self.rfm95.last_rssi}")
                logger.debug(f"\tSNR: {self.rfm95.last_snr}")
                print("Received ACKNOWLEDGEMENT!")            
                print("Motor is open. Closing")
                
        else:
            print("Ok, returning")
            return
    #----------------MAN PAGES----------------------------#    
        
    def help_open(self):
        print("Open the vent for 'x' (sec/min)")
        print("Usage: OPEN x [s/m]")
        print("\t x - number of seconds")
        print("\t [s/m] - specify s or m for seconds or minutes")
        print("To open the vent for 5 minutes")
        print("\tOPEN 5 m")
        print("To open the vent for 10 seconds")
        print("\tOPEN 10 s")
    
    def help_cutdown(self):
        print("Cutdown the balloon")
        print("Usage: cutdown")
        print("This will send a cutdown command to the balloon")
        print("This will not close the vent. You must send a close command to close the vent")
    
    def help_idle(self):
        print("Send an IDLE command to the balloon")
        print("Usage: idle")
        print("This will send an IDLE command to the balloon")
        print("This will do nothing on the balloon. Expect an acknowledgement if the balloon is in range")
    
    def help_close(self):
        print("Close the vent")
        print("Usage: close")
        print("This will send a close command to the balloon")
        print("This will close the vent if it is open. Expect an acknowledgement if the balloon is in range")
    
    def help_set_timeout(self):
        print("Set the receive timeout for the RFM95")
        print("Usage: set_timeout x")
        print("\t x - number of seconds")
        print("This will set the timeout for the RFM95 to 'x' seconds")
        print("This will not affect the balloon. It is only for the ground station")
        print("The default timeout is 5 seconds")
        print("To set the timeout to 10 seconds")
        print("\tset_timeout 10")
        print(f"\nCurrent timeout is {self.RFMtimeout} seconds")
        
    def help_send_custom_packet(self):
        pass
        
    #----------------MISC---------------------------------#    
        
    @handle_assertion
    def do_set_timeout(self, arg):
        assert len(arg) == 1, "Invalid number of arguments. Requires 1. Usage: set_timeout x"
        assert arg.split(' ')[0].isdigit(), "Argument 'x' must be a number"
        timeout = int(arg.split(' ')[0])
        assert timeout > 0, "Timeout must be greater than 0"
        assert timeout < 30, "Timeout must be less than 30 seconds (if you're not getting a response after a 30 second timeout then something is wrong)"
        self.RFMtimeout = timeout
        print(f"Timeout set to {self.RFMtimeout} seconds")
        logger.info(f"Timeout set to {self.RFMtimeout} seconds")
        
    @handle_assertion
    def send_custom_packet(self, arg):
        pass
    
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
