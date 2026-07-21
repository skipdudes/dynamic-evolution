import pygame
import logging
from game.core.state import BaseState

log = logging.getLogger(__name__)

class TestState(BaseState):
    def __init__(self, state_machine):
        super().__init__(state_machine)
        self.pos = pygame.Vector2(816 / 2, 624 / 2)  # initial pos - center of screen
        self.speed = 300.0  # velocity - pixels / sec

    def enter(self):
        log.info("Successfully entered TestState level")

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:  # press ESC - simulate PauseState
                log.info("Pressed ESC key in TestState")

    def update(self, dt: float):
        keys = pygame.key.get_pressed()
        move_dir = pygame.Vector2(0, 0)

        if keys[pygame.K_UP]: move_dir.y -= 1
        if keys[pygame.K_DOWN]: move_dir.y += 1
        if keys[pygame.K_LEFT]: move_dir.x -= 1
        if keys[pygame.K_RIGHT]: move_dir.x += 1

        if move_dir.length() > 0:  # normalize vector, prevent player from moving faster diagonally
            move_dir = move_dir.normalize()

        # Physics: position = direction vector * velocity (per sec) * const dt from game loop (0.01)
        self.pos += move_dir * self.speed * dt

    def draw(self, screen: pygame.Surface):
        screen.fill("purple")
        pygame.draw.circle(screen, "red", self.pos, 24)
