import logging
from game.core.logger import setup_logger
from game.core.engine import Engine
from game.states.splash_state import SplashState

if __name__ == "__main__":
    setup_logger()
    log = logging.getLogger(__name__)
    log.info("Aplication starting...")

    engine = Engine()
    initial_state = SplashState(engine.state_machine)
    engine.state_machine.push(initial_state)
    engine.run()

    log.info("Application shutdown")
