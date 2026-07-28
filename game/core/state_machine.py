import pygame
import logging
from game.core.state import BaseState

log = logging.getLogger(__name__)

class StateMachine:
    def __init__(self):
        self.states: list[BaseState] = []

    def push(self, state: BaseState):
        """Push new state onto state machine (e.g. pause menu)"""
        if self.states:
            pass  # currently on top, possible suspend
        self.states.append(state)
        state.enter()
        log.debug(f"Pushed state: {state.__class__.__name__}. Stack: {[s.__class__.__name__ for s in self.states]}")

    def pop(self):
        """Take state from the top (e.g. resume from pause)"""
        if self.states:
            state = self.states.pop()
            state.exit()
            log.debug(f"Popped state: {state.__class__.__name__}. Stack: {[s.__class__.__name__ for s in self.states]}")
            return state
        return None

    def change(self, state: BaseState):
        """Change current state to a new one (clear stack and put new state, e.g. Menu -> Game)"""
        while self.states:
            self.pop()
        self.push(state)

    def handle_events(self, events: list[pygame.event.Event]):
        """Pass events to the state on top"""
        if self.states:
            self.states[-1].handle_events(events)

    def handle_input(self, keys):
        """Pass continuous key states to the active state."""
        if self.states:
            self.states[-1].handle_input(keys)

    def update(self, dt: float):
        """Update only the top"""
        if self.states:
            self.states[-1].update(dt)

    def draw(self, screen: pygame.Surface):
        """
        Draw states. Later, states can decide whether to draw states underneath
        them (e.g. render background during pause). Atm, draw only the top state.
        """
        if self.states:
            self.states[-1].draw(screen)

    def get_current(self) -> BaseState | None:
        """Returns the current state at the top of the stack, or None if empty."""
        if self.states:
            return self.states[-1]
        return None
