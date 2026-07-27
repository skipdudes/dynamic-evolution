import os
import pygame
from game.core.state import BaseState
from game.core.settings import FONT_UI, IMAGE_ABOUT_BG, KEY_PAUSE, KEY_INTERACT, WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_TEXT_MAIN

class AboutState(BaseState):
    def __init__(self, state_machine, main_menu_state):
        super().__init__(state_machine)
        self.main_menu_state = main_menu_state
        self.font = pygame.font.Font(*FONT_UI)

        self.bg_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        if os.path.exists(IMAGE_ABOUT_BG):
            self.bg_surface = pygame.image.load(IMAGE_ABOUT_BG).convert()
        else:
            self.bg_surface.fill((50, 30, 30))

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_PAUSE or event.key in KEY_INTERACT:
                    self.state_machine.change(self.main_menu_state)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.bg_surface, (0, 0))
        text = self.font.render("About - Shadows of the Crown II", True, COLOR_TEXT_MAIN)  # todo: Move to settings
        screen.blit(text, ((screen.get_width() - text.get_width()) // 2, screen.get_height() // 2))
