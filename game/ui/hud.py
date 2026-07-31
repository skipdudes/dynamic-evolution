import pygame
from game.core.settings import FONT_UI, COLOR_TEXT_MAIN, HUD_NOTIFICATION_DURATION

class HUD:
    def __init__(self):
        # Unpack the tuple (path, size) using *
        self.font_ui = pygame.font.Font(*FONT_UI)

        # List of dictionaries to store active notifications.
        # Format: {"text": str, "timer": float}
        self.notifications = []

    def add_notification(self, text: str, duration: float = HUD_NOTIFICATION_DURATION):
        """Adds a new notification to the queue."""
        self.notifications.append({"text": text, "timer": duration})

    def update(self, dt: float):
        """Updates notification timers and removes expired ones."""
        # Decrease timer for all notifications
        for notif in self.notifications:
            notif["timer"] -= dt

        # Keep only notifications that still have time left
        self.notifications = [n for n in self.notifications if n["timer"] > 0]

    def draw_notifications(self, screen: pygame.Surface):
        """Draws the stack of active notifications in the top-right corner."""
        if not self.notifications:
            return

        padding = 12
        margin_right = 20
        margin_top = 20
        gap = 10  # Gap between multiple notifications

        start_x = screen.get_width() - margin_right
        current_y = margin_top

        for notif in self.notifications:
            text_surf = self.font_ui.render(notif["text"], True, COLOR_TEXT_MAIN)

            rect_w = text_surf.get_width() + (padding * 2)
            rect_h = text_surf.get_height() + (padding * 2)

            x = start_x - rect_w
            y = current_y

            # Fade-out effect during the last 1.0 second
            alpha = 255
            if notif["timer"] < 1.0:
                alpha = max(0, int(notif["timer"] * 255))
                text_surf.set_alpha(alpha)

            # Draw background box with matching alpha
            ui_surface = pygame.Surface((rect_w, rect_h), pygame.SRCALPHA)
            pygame.draw.rect(ui_surface, (0, 0, 0, min(200, alpha)), ui_surface.get_rect(), border_radius=6)
            pygame.draw.rect(ui_surface, (255, 255, 255, min(100, alpha)), ui_surface.get_rect(), 2, border_radius=6)

            screen.blit(ui_surface, (x, y))
            screen.blit(text_surf, (x + padding, y + padding))

            # Shift the Y position down for the next notification in the queue
            current_y += rect_h + gap

    def draw_interaction_prompt(self, screen: pygame.Surface, text: str):
        """Draws a semi-transparent, rounded prompt box at the bottom center."""
        text_surf = self.font_ui.render(text, True, COLOR_TEXT_MAIN)
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
