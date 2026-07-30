import os
import pygame
import logging
from game.core.state import BaseState
from game.core.settings import (
    FONT_UI, FONT_DIALOGUE, KEY_UP, KEY_DOWN, KEY_PAUSE, KEY_INVENTORY,
    WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_TEXT_MAIN, COLOR_TEXT_SELECTED,
    COLOR_TEXT_HELPER, COLOR_MISSING, IMAGES_DIR, STRING_INVENTORY_TITLE,
    STRING_INVENTORY_EMPTY
)

log = logging.getLogger(__name__)

class InventoryState(BaseState):
    def __init__(self, state_machine, play_state):
        super().__init__(state_machine)
        self.play_state = play_state

        self.font_title = pygame.font.Font(FONT_UI[0], 48)
        self.font_list = pygame.font.Font(*FONT_UI)
        self.font_desc = pygame.font.Font(*FONT_DIALOGUE)

        # Extract items as a list of tuples: (item_id, item_data_dict)
        self.items = list(self.play_state.player.inventory.items.items())
        self.selected_index = 0

        self.overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 150))

        # Load and cache item icons (Scaled 2x for Pixel Art: 48x48 -> 96x96)
        self.item_icons = {}
        items_gfx_dir = os.path.join(IMAGES_DIR, "items")

        for item_id, _ in self.items:
            icon_path = os.path.join(items_gfx_dir, f"{item_id}.png")
            if os.path.exists(icon_path):
                img = pygame.image.load(icon_path).convert_alpha()
                # Pygame default scale uses nearest-neighbor (perfect for pixel art)
                self.item_icons[item_id] = pygame.transform.scale(img, (96, 96))
            else:
                log.warning(f"Missing inventory icon for item_id: '{item_id}' at {icon_path}")
                self.item_icons[item_id] = None

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_INVENTORY or event.key in KEY_PAUSE:
                    self.state_machine.pop()

                elif event.key in KEY_UP:
                    if self.items:
                        self.selected_index = (self.selected_index - 1) % len(self.items)
                elif event.key in KEY_DOWN:
                    if self.items:
                        self.selected_index = (self.selected_index + 1) % len(self.items)

    def update(self, dt: float):
        """Allow HUD notifications to continue animating while inventory is open."""
        self.play_state.hud.update(dt)

    def draw(self, screen: pygame.Surface):
        self.play_state.draw(screen)
        screen.blit(self.overlay, (0, 0))

        panel_width, panel_height = 640, 440
        ui_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(ui_surface, (0, 0, 0, 210), ui_surface.get_rect(), border_radius=12)
        pygame.draw.rect(ui_surface, (255, 255, 255, 100), ui_surface.get_rect(), 2, border_radius=12)

        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        screen.blit(ui_surface, (panel_x, panel_y))

        title_surf = self.font_title.render(STRING_INVENTORY_TITLE, True, COLOR_TEXT_SELECTED)
        screen.blit(title_surf, ((WINDOW_WIDTH - title_surf.get_width()) // 2, panel_y + 20))

        pygame.draw.line(screen, COLOR_TEXT_HELPER, (panel_x + 30, panel_y + 80),
                         (panel_x + panel_width - 30, panel_y + 80), 2)

        if not self.items:
            empty_surf = self.font_list.render(STRING_INVENTORY_EMPTY, True, COLOR_TEXT_HELPER)
            screen.blit(empty_surf, ((WINDOW_WIDTH - empty_surf.get_width()) // 2, panel_y + 200))
            return

        # --- Left Side: Item List ---
        list_x = panel_x + 30
        list_y_start = panel_y + 100

        for i, (item_id, data) in enumerate(self.items):
            color = COLOR_TEXT_SELECTED if i == self.selected_index else COLOR_TEXT_MAIN
            text = f"{data['name']} (x{data['quantity']})" if data['quantity'] > 1 else data['name']
            text_surf = self.font_list.render(text, True, color)
            screen.blit(text_surf, (list_x, list_y_start + (i * 40)))

        pygame.draw.line(screen, COLOR_TEXT_HELPER, (panel_x + 280, panel_y + 100),
                         (panel_x + 280, panel_y + panel_height - 30), 2)

        # --- Right Side: Item Details ---
        details_x = panel_x + 310
        details_y = panel_y + 100

        selected_item_id = self.items[self.selected_index][0]
        selected_item_data = self.items[self.selected_index][1]

        # 1. Draw Icon (96x96)
        icon_size = 96
        icon_rect = pygame.Rect(details_x, details_y, icon_size, icon_size)
        icon_surface = self.item_icons.get(selected_item_id)

        if icon_surface:
            screen.blit(icon_surface, (details_x, details_y))
            pygame.draw.rect(screen, COLOR_TEXT_HELPER, icon_rect, 1, border_radius=4)
        else:
            pygame.draw.rect(screen, COLOR_MISSING, icon_rect, border_radius=4)
            pygame.draw.rect(screen, COLOR_TEXT_HELPER, icon_rect, 1, border_radius=4)

        # 2. Detail Name (Wrapped text to the right of the icon)
        name_x = details_x + icon_size + 16
        name_width = (panel_width - 310) - icon_size - 30

        name_rect = pygame.Rect(name_x, details_y, name_width, 200)
        final_name_y = self._draw_text_wrapped(screen, selected_item_data['name'], self.font_list, COLOR_TEXT_SELECTED,
                                               name_rect)

        # 3. Description (Wrapped text placed safely below the icon AND the name)
        desc_y = max(details_y + icon_size, final_name_y) + 16
        desc_rect = pygame.Rect(details_x, desc_y, panel_width - 340, panel_height - (desc_y - panel_y) - 10)

        self._draw_text_wrapped(screen, selected_item_data['description'], self.font_desc, COLOR_TEXT_MAIN, desc_rect)

        # Draw active notifications ON TOP of the inventory menu
        self.play_state.hud.draw_notifications(screen)

    def _draw_text_wrapped(self, surface: pygame.Surface, text: str, font: pygame.font.Font, color: tuple,
                           rect: pygame.Rect) -> int:
        """
        Draws word-wrapped text within a bounding rect.
        Returns the final Y position after the last line is drawn.
        """
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width, _ = font.size(test_line)
            if test_width <= rect.width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        y_offset = rect.y
        for line in lines:
            text_surface = font.render(line, True, color)
            surface.blit(text_surface, (rect.x, y_offset))
            y_offset += font.get_height()

        return y_offset
