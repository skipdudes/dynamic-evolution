import pygame
from game.core.state import BaseState
from game.core.settings import WINDOW_WIDTH, WINDOW_HEIGHT

class TransitionState(BaseState):
    def __init__(self, state_machine, prev_state, next_state=None, next_state_func=None, duration=0.5, is_quit=False):
        super().__init__(state_machine)
        self.prev_state = prev_state
        self.next_state = next_state
        self.next_state_func = next_state_func
        self.duration = duration
        self.is_quit = is_quit

        self.alpha = 0.0
        self.fading_in = False

        self.fade_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.fade_surface.fill((0, 0, 0))

    def handle_events(self, events: list[pygame.event.Event]):
        pass  # block all events during transition

    def handle_input(self, keys):
        pass  # block all input during transition

    def update(self, dt: float):
        fade_speed = 255.0 / self.duration

        if not self.fading_in:
            self.alpha += fade_speed * dt
            if self.alpha >= 255.0:
                self.alpha = 255.0
                self.fading_in = True

                if self.is_quit:  # if the transition is to quit the game
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                elif self.next_state_func:
                    self.next_state = self.next_state_func()  # pure black screen - load new level & API
        else:
            self.alpha -= fade_speed * dt
            if self.alpha <= 0.0:
                self.alpha = 0.0
                if self.next_state:  # transition complete, activate the next state permanently
                    self.state_machine.change(self.next_state)

    def draw(self, screen: pygame.Surface):
        if not self.fading_in and self.prev_state:
            self.prev_state.draw(screen)
        elif self.fading_in and self.next_state:
            self.next_state.draw(screen)

        self.fade_surface.set_alpha(int(self.alpha))
        screen.blit(self.fade_surface, (0, 0))
