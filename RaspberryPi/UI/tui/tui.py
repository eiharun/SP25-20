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
    def __init__(self):
        constructor = RFM95Wrapper()
        self.rfm95 = constructor.construct()
        logger.debug("RFM95 Constructed")

    def run(self):
        try:
            logger.info("Starting TUI")
            print("Starting TUI")
            tui_command = TUICommand(self.rfm95)
            tui_command.cmdloop()
        except KeyboardInterrupt:
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
        self.intro = "Welcome to the RFM95 CLI. Type help or ? to list commands.\n"
        self.intro += "Type 'exit' to exit the CLI.\n"
        self.intro += "Type 'help <command>' for help on a specific command.\n"
        self.intro += "Type 'clear' to clear the screen.\n"
        
    def default(self, line):
        print(f"Unknown command: {line}")
        
    def do_exit(self, arg):
         """Exits the shell."""
         return True
     
    def do_help(self, arg):
        return super().do_help(arg)
    
    def do_clear(self, arg):
        """Clears the screen."""
        print("\033[H\033[J", end="")
        print(self.intro)
        return False