import logging
from game.core.logger import setup_logger
from game.core.engine import Engine
from game.entities.player import Player
from game.states.play_state import PlayState

if __name__ == "__main__":
    setup_logger()
    log = logging.getLogger(__name__)
    log.info("Aplication starting...")

    engine = Engine()
    global_player = Player(x=0, y=0)

    initial_state = PlayState(
        engine.state_machine,
        level_filename="oldworld.tmx",
        player_instance=global_player
    )
    engine.state_machine.change(initial_state)

    engine.run()

    log.info("Application shutdown")
