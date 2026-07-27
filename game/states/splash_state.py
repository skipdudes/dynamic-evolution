import pygame
from game.core.state import BaseState
from game.core.settings import FONT_SPLASH, STRING_SPLASH_TEXT, COLOR_TEXT_MAIN
from game.states.transition_state import TransitionState

class SplashState(BaseState):
    def __init__(self, state_machine):
        super().__init__(state_machine)
        self.font = pygame.font.Font(*FONT_SPLASH)
        self.text_surf = self.font.render(STRING_SPLASH_TEXT, True, COLOR_TEXT_MAIN)

        self.alpha = 0.0
        self.fading_in = True
        self.timer = 0.0
        self.hold_time = 1.5
        self.fade_speed = 250.0

    def update(self, dt: float):
        if self.fading_in:
            self.alpha += self.fade_speed * dt
            if self.alpha >= 255.0:
                self.alpha = 255.0
                self.fading_in = False
        else:
            self.timer += dt
            if self.timer >= self.hold_time:
                self.alpha -= self.fade_speed * dt
                if self.alpha <= 0.0:
                    self.alpha = 0.0

                    # Delay import to avoid circular dependencies if necessary
                    from game.states.main_menu_state import MainMenuState
                    next_state = MainMenuState(self.state_machine)
                    transition = TransitionState(self.state_machine, self, next_state, duration=0.5)
                    self.state_machine.change(transition)

    def draw(self, screen: pygame.Surface):
        screen.fill((0, 0, 0))
        self.text_surf.set_alpha(int(self.alpha))

        x = (screen.get_width() - self.text_surf.get_width()) // 2
        y = (screen.get_height() - self.text_surf.get_height()) // 2
        screen.blit(self.text_surf, (x, y))
