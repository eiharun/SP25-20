pyimport argparse
import logging
from tui import TUI
from gui import GUI

logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(usage="python3 -m UI [-h] [-t] [-D]",description="User Interface for Ground Station. By Default the GUI will launch")
    parser.add_argument("-t", "--tui", action="store_true", help="Launch textual user interface instead of GUI")
    parser.add_argument("-D", "--debug", action="store_true", help="Enable debug logging")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s %(message)s")
    tui = args.tui
    logger.info("Starting Program")
    if tui:
        logger.info("Starting TUI")
        tui = TUI()
        tui.run()
    else:
        #run the by default gui
        logger.info("Starting GUI")
        gui = GUI()
        gui.run()