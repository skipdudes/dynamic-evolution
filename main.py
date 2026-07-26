import logging
from game.core.logger import setup_logger
from game.core.engine import Engine
from game.entities.player import Player
from game.core.game_state import GameState
from game.states.play_state import PlayState

if __name__ == "__main__":
    setup_logger()
    log = logging.getLogger(__name__)
    log.info("Aplication starting...")

    engine = Engine()
    player = Player(x=0, y=0)
    game_state = GameState()

    initial_state = PlayState(
        engine.state_machine,
        level_filename="castle.tmx",
        player_instance=player,
        game_state=game_state
    )
    engine.state_machine.change(initial_state)

    engine.run()

    log.info("Application shutdown")
