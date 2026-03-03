from game.logger import setup_logger
from game.loop import Game
import logging

if __name__ == "__main__":
    setup_logger()
    log = logging.getLogger(__name__)

    log.info("Program entry point")

    game = Game()
    game.run()
