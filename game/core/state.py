import pygame

class BaseState:
    def __init__(self, state_machine):
        self.state_machine = state_machine  # state machine access so it can pop itself or push another state

    def handle_events(self, events: list[pygame.event.Event]):
        """Capture user input (only for active state)"""
        pass

    def update(self, dt: float):
        """Update logic (position, variables, time)"""
        pass

    def draw(self, screen: pygame.Surface):
        """Draw state elements on screen"""
        pass

    def enter(self):
        """Called once upon being pushed"""
        pass

    def exit(self):
        """Called once upon being popped"""
        pass
