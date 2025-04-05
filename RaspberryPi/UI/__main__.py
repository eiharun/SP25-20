import argparse
import logging
from .tui import TUI

logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--tui", help="Launch textual user interface")
    parser.add_argument("-D", "--debug", action="store_true", help="Enable debug logging")

if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s %(message)s")
    tui = args.tui
    if tui:
        logger.info("Starting TUI")
        tui = TUI()
        tui.run()
    else:
        #gui
        pass