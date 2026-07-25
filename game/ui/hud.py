import pygame
from game.core.settings import FONT_UI

class HUD:
    def __init__(self):
        # Unpack the tuple (path, size) using *
        self.font_ui = pygame.font.Font(*FONT_UI)

    def draw_interaction_prompt(self, screen: pygame.Surface, text: str):
        """Draws a semi-transparent, rounded prompt box at the bottom center."""
        text_surf = self.font_ui.render(text, True, (255, 255, 255))
        padding = 15

        rect_w = text_surf.get_width() + (padding * 2)
        rect_h = text_surf.get_height() + (padding * 2)

        x = (screen.get_width() - rect_w) // 2
        y = screen.get_height() - rect_h - 20  # 20px offset from the bottom

        # Draw alpha rounded rect
        ui_surface = pygame.Surface((rect_w, rect_h), pygame.SRCALPHA)
        pygame.draw.rect(ui_surface, (0, 0, 0, 200), ui_surface.get_rect(), border_radius=8)
        pygame.draw.rect(ui_surface, (255, 255, 255, 100), ui_surface.get_rect(), 2, border_radius=8)

        # Blit to screen
        screen.blit(ui_surface, (x, y))
        screen.blit(text_surf, (x + padding, y + padding))
