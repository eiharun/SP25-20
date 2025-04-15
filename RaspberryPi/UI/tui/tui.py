from rfm95api import *
import logging
import cmd
from threading import Thread, Lock, Event, Condition
import time
import readline
import sys

logger = logging.getLogger(__name__)

class TUI:
    """
    Texual User Interface allows more contol over application in comparison to the GUI.
    It also allows ease of testing.
    """
    def __init__(self):
        constructor = RFM95Wrapper()
        self.rfm95 = constructor.construct()
        self.rfm_lock = Lock()
        self.priority_event = Event()
        self.exit_event = Event()
        self._idleThread = Thread(target=self.look_for_idle)
        logger.debug("RFM95 Constructed")

    def look_for_idle(self):
        while not self.exit_event.is_set():
            if self.priority_event.is_set():
                time.sleep(0.1)
                continue
            if not self.rfm_lock.acquire(timeout=0.1):
                continue
            try:
                if self.priority_event.is_set():
                    continue
                idle = self.rfm95.receive(timeout=3)
                if idle:
                    saved_line = readline.get_line_buffer()
                    # saved_pos = readline.get_point() 
                    sys.stdout.write("\r")  # Go to line start
                    sys.stdout.write("\033[K")  # Clear the line
                    print(f'Idle Recieved! Balloon in Range\t\a#{idle[0]}')
                    sys.stdout.write(f"\nRFM95> {saved_line}")
                    sys.stdout.flush()
                    readline.redisplay()
                    # with open("idle.log", 'a') as f:
                    #     print("\a")
                    #     f.write(f"[{time.strftime('%H:%M:%S')}] Ping received: {idle}\n")
                    # print(f"Idle: {idle}\nRFM95> ", end='', flush=True)#TODO Make output cleaner
            finally:
                self.rfm_lock.release()
            # time.sleep(0.1)

    def run(self):
        try:
            f = open("idle.log", 'w')
            f.close()
            logger.debug("Starting TUI")
            print("Starting TUI")
            tui_command = TUICommand(self.rfm95, self.rfm_lock, self.priority_event)
            self._idleThread.start()
            tui_command.cmdloop()
        except KeyboardInterrupt:
            print()
            self.exit_event.set()
            self._idleThread.join()
            logger.debug("Exiting Ground Station TUI")
            print("Exiting Ground Station TUI")
            exit(0)
            
class TUICommand(cmd.Cmd):
    """
    Command line interface for the RFM95 wrapper.
    """
    prompt = "RFM95> "
    
    def __init__(self, rfm95, radio_lock, priority_event):
        super().__init__()
        self.rfm95 = rfm95
        self._rfm_lock = radio_lock
        self._priority_event = priority_event
        
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
        self._priority_event.set()
        assert len(arg.split(' ')) == 2
        duration = int(arg.split(' ')[0])
        unit = arg.split(' ')[1].lower()
        assert unit == 's' or unit == 'm'
        print(f"Opening vent for {duration} {'seconds' if unit == 's' else 'minutes'}")
        cmd = 0
        if unit == 's':
            cmd = Commands.OPENs.value
        elif unit == 'm':
            cmd = Commands.OPENm.value
        assert cmd != 0
        num_bytes, payload = self.byte_w_len(duration)
        logger.debug(f"Verification: {duration}:{payload}:{num_bytes}:{int.from_bytes(payload,'big')}")
        #TODO: Wait for idle
        try:
            with self._rfm_lock:
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
        finally:
            self._priority_event.clear()
        
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
        
    def preloop(self):
        """Initialization before the command loop starts."""
        print("Starting the CLI...")
        
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
        
    # def byte_length(self,i):
        # return (i.bit_length() + 7) // 8

    def byte_w_len(self, i:int):
        """
        Returns the number of bytes and the byte array of the given String.
        """
        assert isinstance(i, int), "Argument in byte_w_len() must be a string"
        num_bytes = (i.bit_length() + 7) // 8
        return num_bytes, i.to_bytes(num_bytes, byteorder='big')
        