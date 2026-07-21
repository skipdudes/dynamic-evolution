import pygame
import logging
import time
from game.core.state_machine import StateMachine

log = logging.getLogger(__name__)

class Engine:
    def __init__(self, width: int = 816, height: int = 624):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Shadows of the Crown II")

        self.clock = pygame.time.Clock()
        self.running = True

        self.target_fps = 60  # future menu target FPS (30, 60, 120, 0 = no limit)
        self.state_machine = StateMachine()

    def run(self):
        log.info("Starting the game loop")

        MS_PER_UPDATE = 0.01  # Fixed Update Time Step - 10 ms (0.01 s)
        previous_time = time.perf_counter()
        lag = 0.0

        while self.running:
            # Calculate time and accumulator
            current_time = time.perf_counter()
            elapsed = current_time - previous_time
            previous_time = current_time
            lag += elapsed

            if lag > 0.2:  # if game stuck for too long, don't let update too much
                lag = 0.2

            # Get and handle events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            self.state_machine.handle_events(events)

            # Update logic, as many "packets" as in accumulator
            while lag >= MS_PER_UPDATE:
                self.state_machine.update(MS_PER_UPDATE)
                lag -= MS_PER_UPDATE

            # Render
            self.state_machine.draw(self.screen)
            pygame.display.flip()

            self.clock.tick(self.target_fps)

        self.quit()

    def quit(self):
        log.info("Finished the game loop")
        pygame.quit()
