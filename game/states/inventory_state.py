import os
import pygame
import logging
from game.core.state import BaseState
from game.core.settings import (
    FONT_UI, FONT_DIALOGUE, KEY_UP, KEY_DOWN, KEY_RETURN, KEY_INVENTORY, KEY_INTERACT,
    WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_TEXT_MAIN, COLOR_TEXT_SELECTED,
    COLOR_TEXT_HELPER, COLOR_MISSING, IMAGES_DIR, STRING_INVENTORY_TITLE,
    STRING_INVENTORY_EMPTY, STRING_DIALOGUE_SCROLL_UP, STRING_DIALOGUE_SCROLL_DOWN,
    STRING_NOTIFY_QUEST, STRING_BREAK_SEAL_LOG_ENTRY, STRING_BREAK_SEAL_PROMPT
)
from game.entities.item_data import ITEMS_DB
from game.entities.quest_data import QUESTS_DB

log = logging.getLogger(__name__)

class InventoryState(BaseState):
    def __init__(self, state_machine, play_state):
        super().__init__(state_machine)
        self.play_state = play_state

        self.font_title = pygame.font.Font(FONT_UI[0], 48)
        self.font_list = pygame.font.Font(*FONT_UI)
        self.font_desc = pygame.font.Font(*FONT_DIALOGUE)
        self.font_ui = pygame.font.Font(*FONT_UI)

        # Load scroll icons
        self.icon_scroll_up = self._load_icon("scroll_up.png")
        self.icon_scroll_down = self._load_icon("scroll_down.png")

        self.selected_index = 0
        self.list_scroll_offset = 0
        self.max_list_items = 8

        self.overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 150))

        self.items = []
        self.item_icons = {}

        # Initial inventory load
        self._refresh_inventory()

    def _load_icon(self, filename: str) -> pygame.Surface | None:
        """Loads optional scroll arrow icons from assets/images/ui/"""
        path = os.path.join(IMAGES_DIR, "ui", filename)
        if os.path.exists(path):
            return pygame.image.load(path).convert_alpha()
        return None

    def _load_item_icon(self, item_id: str):
        """Helper to load a specific item's icon if not already loaded."""
        if item_id in self.item_icons:
            return

        items_gfx_dir = os.path.join(IMAGES_DIR, "items")
        item_info = ITEMS_DB.get(item_id, {})
        custom_icon_name = item_info.get("icon")

        final_icon_path = None

        # 1. Try custom icon from ITEMS_DB
        if custom_icon_name:
            temp_path = os.path.join(items_gfx_dir, custom_icon_name)
            if os.path.exists(temp_path):
                final_icon_path = temp_path

        # 2. If custom fails or is missing, try item_id.png fallback
        if not final_icon_path:
            temp_path = os.path.join(items_gfx_dir, f"{item_id}.png")
            if os.path.exists(temp_path):
                final_icon_path = temp_path

        # 3. Load the matched image, or fallback to missing texture
        if final_icon_path:
            img = pygame.image.load(final_icon_path).convert_alpha()
            self.item_icons[item_id] = pygame.transform.scale(img, (96, 96))
        else:
            log.warning(f"Missing inventory icon for item_id: '{item_id}'. Falling back to missing texture.")
            self.item_icons[item_id] = None

    def _refresh_inventory(self):
        """Refreshes the item list and loads missing icons without closing the UI."""
        self.items = list(self.play_state.player.inventory.items.items())
        for item_id, _ in self.items:
            self._load_item_icon(item_id)

        # Secure the index in case the last item in the list was removed
        if self.items and self.selected_index >= len(self.items):
            self.selected_index = max(0, len(self.items) - 1)

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_INVENTORY or event.key in KEY_RETURN:
                    self.state_machine.pop()

                # Interaction logic (e.g., opening the sealed letter)
                elif event.key in KEY_INTERACT:
                    if self.items:
                        selected_item_id = self.items[self.selected_index][0]

                        if selected_item_id == "sealed_letter":
                            log.info("Player decided to break the seal on the letter!")
                            self.play_state.player.inventory.remove_item("sealed_letter", 1)
                            self.play_state.player.inventory.add_item("opened_letter", 1)
                            self.play_state.player.journal.add_entry("quest_midnight_drop", STRING_BREAK_SEAL_LOG_ENTRY)
                            quest_name = QUESTS_DB.get("quest_midnight_drop", {}).get("title", "quest_midnight_drop")
                            self.play_state.hud.add_notification(f"{STRING_NOTIFY_QUEST}{quest_name}")
                            self._refresh_inventory()  # refresh the UI to immediately show 'opened_letter'

                elif event.key in KEY_UP:
                    if self.items:
                        self.selected_index = (self.selected_index - 1) % len(self.items)
                        self._adjust_scroll()
                elif event.key in KEY_DOWN:
                    if self.items:
                        self.selected_index = (self.selected_index + 1) % len(self.items)
                        self._adjust_scroll()

    def _adjust_scroll(self):
        if self.selected_index < self.list_scroll_offset:
            self.list_scroll_offset = self.selected_index
        elif self.selected_index >= self.list_scroll_offset + self.max_list_items:
            self.list_scroll_offset = self.selected_index - self.max_list_items + 1

    def update(self, dt: float):
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

        visible_items = self.items[self.list_scroll_offset: self.list_scroll_offset + self.max_list_items]

        for i, (item_id, data) in enumerate(visible_items):
            actual_index = self.list_scroll_offset + i
            color = COLOR_TEXT_SELECTED if actual_index == self.selected_index else COLOR_TEXT_MAIN
            text = f"{data['name']} (x{data['quantity']})" if data['quantity'] > 1 else data['name']
            text_surf = self.font_list.render(text, True, color)
            screen.blit(text_surf, (list_x, list_y_start + (i * 40)))

        # List Scroll indicators (Icons)
        if self.list_scroll_offset > 0:
            if self.icon_scroll_up:
                screen.blit(self.icon_scroll_up, (panel_x + 130, panel_y + 85))
            else:
                screen.blit(self.font_ui.render(STRING_DIALOGUE_SCROLL_UP, True, COLOR_TEXT_HELPER),
                            (list_x, panel_y + 70))

        if self.list_scroll_offset + self.max_list_items < len(self.items):
            if self.icon_scroll_down:
                screen.blit(self.icon_scroll_down, (panel_x + 130, panel_y + panel_height - 25))
            else:
                screen.blit(self.font_ui.render(STRING_DIALOGUE_SCROLL_DOWN, True, COLOR_TEXT_HELPER),
                            (list_x, panel_y + panel_height - 25))

        pygame.draw.line(screen, COLOR_TEXT_HELPER, (panel_x + 280, panel_y + 100),
                         (panel_x + 280, panel_y + panel_height - 30), 2)

        # --- Right Side: Item Details ---
        details_x = panel_x + 310
        details_y = panel_y + 100

        selected_item_id = self.items[self.selected_index][0]
        selected_item_data = self.items[self.selected_index][1]

        # 1. Draw Icon
        icon_size = 96
        icon_rect = pygame.Rect(details_x, details_y, icon_size, icon_size)
        icon_surface = self.item_icons.get(selected_item_id)

        if icon_surface:
            screen.blit(icon_surface, (details_x, details_y))
            pygame.draw.rect(screen, COLOR_TEXT_HELPER, icon_rect, 1, border_radius=4)
        else:
            pygame.draw.rect(screen, COLOR_MISSING, icon_rect, border_radius=4)
            pygame.draw.rect(screen, COLOR_TEXT_HELPER, icon_rect, 1, border_radius=4)

        # 2. Detail Name
        name_x = details_x + icon_size + 16
        name_width = (panel_width - 310) - icon_size - 30
        name_rect = pygame.Rect(name_x, details_y, name_width, 200)
        final_name_y = self._draw_text_wrapped(screen, selected_item_data['name'], self.font_list, COLOR_TEXT_SELECTED,
                                               name_rect)

        # 3. Description
        desc_y = max(details_y + icon_size, final_name_y) + 16
        desc_rect = pygame.Rect(details_x, desc_y, panel_width - 340, panel_height - (desc_y - panel_y) - 10)
        self._draw_text_wrapped(screen, selected_item_data['description'], self.font_desc, COLOR_TEXT_MAIN, desc_rect)

        # 4. Bottom UI hint
        if selected_item_id == "sealed_letter":
            hint_surf = self.font_ui.render(STRING_BREAK_SEAL_PROMPT, True, COLOR_TEXT_HELPER)
            screen.blit(hint_surf, ((WINDOW_WIDTH - hint_surf.get_width()) // 2, panel_y + panel_height + 10))

    def _draw_text_wrapped(self, surface: pygame.Surface, text: str, font: pygame.font.Font, color: tuple,
                           rect: pygame.Rect) -> int:
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= rect.width:
                current_line.append(word)
            else:
                if current_line: lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))

        y_offset = rect.y
        for line in lines:
            text_surface = font.render(line, True, color)
            surface.blit(text_surface, (rect.x, y_offset))
            y_offset += font.get_height()

        return y_offset
