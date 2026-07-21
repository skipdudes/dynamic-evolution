import logging
from game.core.logger import setup_logger
from game.core.engine import Engine
from game.states.test_state import TestState

if __name__ == "__main__":
    setup_logger()
    log = logging.getLogger(__name__)
    log.info("Program entry point")

    engine = Engine()
    test_state = TestState(engine.state_machine)  # create and test TestState with state machine
    engine.state_machine.change(test_state)  # push state
    engine.run()  # run game

    log.info("Application shutdown")
