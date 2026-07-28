import os
import pygame
from game.core.state import BaseState
from game.core.settings import (
    FONT_UI, FONT_DIALOGUE, IMAGE_ABOUT_BG, KEY_PAUSE, KEY_INTERACT,
    GAME_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_TEXT_SELECTED,
    COLOR_TEXT_MAIN, COLOR_TEXT_HELPER, STRING_ABOUT_TITLE, STRING_ABOUT_TEXT,
    STRING_ABOUT_BACK
)

class AboutState(BaseState):
    def __init__(self, state_machine):
        super().__init__(state_machine)

        self.font_title = pygame.font.Font(FONT_UI[0], 48)
        self.font_text = pygame.font.Font(*FONT_DIALOGUE)
        self.font_info = pygame.font.Font(*FONT_DIALOGUE)

        self.bg_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        if os.path.exists(IMAGE_ABOUT_BG):
            self.bg_surface = pygame.image.load(IMAGE_ABOUT_BG).convert()
        else:
            self.bg_surface.fill((50, 30, 30))

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_PAUSE or event.key in KEY_INTERACT:
                    self.state_machine.pop()

    def draw(self, screen: pygame.Surface):
        screen.blit(self.bg_surface, (0, 0))

        panel_width, panel_height = 500, 400
        ui_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(ui_surface, (0, 0, 0, 200), ui_surface.get_rect(), border_radius=12)

        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        screen.blit(ui_surface, (panel_x, panel_y))

        # Title
        title_surf = self.font_title.render(STRING_ABOUT_TITLE, True, COLOR_TEXT_SELECTED)
        screen.blit(title_surf, ((WINDOW_WIDTH - title_surf.get_width()) // 2, panel_y + 30))

        # Main Text
        lines = STRING_ABOUT_TEXT.split('\n')
        line_height = self.font_text.get_height() + 8  # Slightly tighter spacing
        start_y = panel_y + 90  # Shifted up to fit more lines comfortably

        for i, line in enumerate(lines):
            line_surf = self.font_text.render(line.strip(), True, COLOR_TEXT_MAIN)
            x = (WINDOW_WIDTH - line_surf.get_width()) // 2
            y = start_y + (i * line_height)
            screen.blit(line_surf, (x, y))

        # Ogonek hack: 'e' + ',' = 'ę'
        comma_surf = self.font_text.render(",", True, COLOR_TEXT_MAIN)
        comma_x = WINDOW_WIDTH // 2 + 12
        comma_y = start_y + (3 * line_height)
        screen.blit(comma_surf, (comma_x, comma_y))

        prompt_surf = self.font_info.render(STRING_ABOUT_BACK, True, COLOR_TEXT_HELPER)
        screen.blit(prompt_surf, ((WINDOW_WIDTH - prompt_surf.get_width()) // 2, panel_y + panel_height - 60))

        version_surf = self.font_info.render(f"v{GAME_VERSION}", True, COLOR_TEXT_HELPER)
        screen.blit(version_surf,
                    (WINDOW_WIDTH - version_surf.get_width() - 20, WINDOW_HEIGHT - version_surf.get_height() - 15))
