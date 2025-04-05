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
        duration = arg.split(' ')[0]
        unit = arg.split(' ')[1].lower()
        assert unit == 's' or unit == 'm'
        if not self.verify_send_on_idle():
            return
        print("Waiting for IDLE (balloon to be in range)")
        print(f"Opening vent for {duration} {'seconds' if unit == 's' else 'minutes'}")
        
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