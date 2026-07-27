import logging
from game.core.logger import setup_logger
from game.core.engine import Engine
from game.states.splash_state import SplashState
from game.core.game_state import GameState
from game.entities.player import Player
from game.states.play_state import PlayState

if __name__ == "__main__":
    setup_logger()
    log = logging.getLogger(__name__)
    log.info("Aplication starting...")

    engine = Engine()
    initial_state = SplashState(engine.state_machine)
    engine.state_machine.push(initial_state)
    engine.run()

    # # Debug
    # engine = Engine()
    # game_state = GameState()
    # player = Player(x=0, y=0)
    # play_state = PlayState(
    #     engine.state_machine,
    #     level_filename="castle.tmx",
    #     player_instance=player,
    #     game_state=game_state
    # )
    # engine.state_machine.push(play_state)
    # engine.run()

    log.info("Application shutdown")
