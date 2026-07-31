import os
import pygame
from game.core.state import BaseState
from game.core.settings import (
    IMAGES_DIR, FONT_UI, FONT_DIALOGUE, KEY_UP, KEY_DOWN, KEY_RETURN, KEY_JOURNAL, KEY_INTERACT,
    WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_TEXT_MAIN, COLOR_TEXT_SELECTED,
    COLOR_TEXT_HELPER, STRING_JOURNAL_TITLE,
    STRING_JOURNAL_EMPTY, STRING_JOURNAL_ACTIVE, STRING_JOURNAL_COMPLETED,
    STRING_DIALOGUE_SCROLL_UP, STRING_DIALOGUE_SCROLL_DOWN, STRING_RETURN_PROMPT,
    STRING_JOURNAL_READ_PROMPT
)

class JournalState(BaseState):
    def __init__(self, state_machine, play_state):
        super().__init__(state_machine)
        self.play_state = play_state

        self.font_title = pygame.font.Font(FONT_UI[0], 48)
        self.font_list = pygame.font.Font(*FONT_UI)
        self.font_desc = pygame.font.Font(*FONT_DIALOGUE)
        self.font_ui = pygame.font.Font(*FONT_UI)  # Fixed missing font error

        # Load scroll icons
        self.icon_scroll_up = self._load_icon("scroll_up.png")
        self.icon_scroll_down = self._load_icon("scroll_down.png")

        self.quests = list(self.play_state.player.journal.quests.items())[::-1]

        self.focus = "list"
        self.selected_index = 0

        self.list_scroll_offset = 0
        self.max_list_items = 9

        # We start by snapping to the newest entry for the initially selected quest
        self.entries_scroll_offset = 9999
        self.max_entry_lines = 11

        self.overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 150))

    def _load_icon(self, filename: str) -> pygame.Surface | None:
        """Loads optional scroll arrow icons from assets/images/ui/"""
        path = os.path.join(IMAGES_DIR, "ui", filename)
        if os.path.exists(path):
            return pygame.image.load(path).convert_alpha()
        return None

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:

                if event.key in KEY_RETURN:
                    if self.focus == "details":
                        self.focus = "list"
                    else:
                        self.state_machine.pop()

                elif event.key in KEY_JOURNAL:
                    self.state_machine.pop()

                elif event.key in KEY_INTERACT:
                    if self.focus == "list" and self.quests:
                        self.focus = "details"

                elif event.key in KEY_UP:
                    if self.focus == "list" and self.quests:
                        self.selected_index = (self.selected_index - 1) % len(self.quests)
                        self._adjust_list_scroll()
                        self.entries_scroll_offset = 9999  # Snap preview to the newest entry
                    elif self.focus == "details":
                        self.entries_scroll_offset -= 1

                elif event.key in KEY_DOWN:
                    if self.focus == "list" and self.quests:
                        self.selected_index = (self.selected_index + 1) % len(self.quests)
                        self._adjust_list_scroll()
                        self.entries_scroll_offset = 9999  # Snap preview to the newest entry
                    elif self.focus == "details":
                        self.entries_scroll_offset += 1

    def _adjust_list_scroll(self):
        if self.selected_index < self.list_scroll_offset:
            self.list_scroll_offset = self.selected_index
        elif self.selected_index >= self.list_scroll_offset + self.max_list_items:
            self.list_scroll_offset = self.selected_index - self.max_list_items + 1

    def update(self, dt: float):
        self.play_state.hud.update(dt)

    def _wrap_text_to_lines(self, text: str, font: pygame.font.Font, max_width: int) -> list[str]:
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line: lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def draw(self, screen: pygame.Surface):
        self.play_state.draw(screen)
        screen.blit(self.overlay, (0, 0))

        panel_width, panel_height = 680, 480
        ui_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(ui_surface, (0, 0, 0, 210), ui_surface.get_rect(), border_radius=12)

        border_color = COLOR_TEXT_SELECTED if self.focus == "details" else (255, 255, 255, 100)
        pygame.draw.rect(ui_surface, border_color, ui_surface.get_rect(), 2, border_radius=12)

        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        screen.blit(ui_surface, (panel_x, panel_y))

        title_surf = self.font_title.render(STRING_JOURNAL_TITLE, True, COLOR_TEXT_SELECTED)
        screen.blit(title_surf, ((WINDOW_WIDTH - title_surf.get_width()) // 2, panel_y + 20))

        pygame.draw.line(screen, COLOR_TEXT_HELPER, (panel_x + 30, panel_y + 80),
                         (panel_x + panel_width - 30, panel_y + 80), 2)

        if not self.quests:
            empty_surf = self.font_list.render(STRING_JOURNAL_EMPTY, True, COLOR_TEXT_HELPER)
            screen.blit(empty_surf, ((WINDOW_WIDTH - empty_surf.get_width()) // 2, panel_y + 200))
            return

        # --- Left Side: Quest List ---
        list_x = panel_x + 30
        list_y_start = panel_y + 100

        visible_quests = self.quests[self.list_scroll_offset: self.list_scroll_offset + self.max_list_items]

        for i, (q_id, q_data) in enumerate(visible_quests):
            actual_index = self.list_scroll_offset + i
            is_selected = (actual_index == self.selected_index)
            is_active = (q_data["status"] == "active")

            if is_selected:
                color = COLOR_TEXT_SELECTED
            elif is_active:
                color = COLOR_TEXT_MAIN
            else:
                color = COLOR_TEXT_HELPER

            if self.focus == "details" and not is_selected:
                color = COLOR_TEXT_HELPER

            text_surf = self.font_list.render(q_data['title'], True, color)
            screen.blit(text_surf, (list_x, list_y_start + (i * 40)))

        # List Scroll indicators (Icons)
        if self.list_scroll_offset > 0:
            if self.icon_scroll_up:
                screen.blit(self.icon_scroll_up, (panel_x + 150, panel_y + 85))
            else:
                screen.blit(self.font_ui.render(STRING_DIALOGUE_SCROLL_UP, True, COLOR_TEXT_HELPER),
                            (list_x, panel_y + 70))

        if self.list_scroll_offset + self.max_list_items < len(self.quests):
            if self.icon_scroll_down:
                screen.blit(self.icon_scroll_down, (panel_x + 150, panel_y + panel_height - 25))
            else:
                screen.blit(self.font_ui.render(STRING_DIALOGUE_SCROLL_DOWN, True, COLOR_TEXT_HELPER),
                            (list_x, panel_y + panel_height - 25))

        pygame.draw.line(screen, COLOR_TEXT_HELPER, (panel_x + 280, panel_y + 100),
                         (panel_x + 280, panel_y + panel_height - 30), 2)

        # --- Right Side: Quest Details ---
        details_x = panel_x + 310
        details_y = panel_y + 100
        text_max_width = panel_width - 340

        selected_q_data = self.quests[self.selected_index][1]
        is_active = (selected_q_data["status"] == "active")

        # 1. Title & Status
        title_lines = self._wrap_text_to_lines(selected_q_data['title'], self.font_list, text_max_width)
        current_y = details_y
        for line in title_lines:
            screen.blit(self.font_list.render(line, True, COLOR_TEXT_SELECTED), (details_x, current_y))
            current_y += self.font_list.get_height()

        status_text = STRING_JOURNAL_ACTIVE if is_active else STRING_JOURNAL_COMPLETED
        status_color = COLOR_TEXT_MAIN if is_active else COLOR_TEXT_HELPER
        screen.blit(self.font_desc.render(status_text, True, status_color), (details_x, current_y + 5))

        current_y += 35

        # 2. Entries
        all_entry_lines = []
        for entry in selected_q_data["entries"]:
            bullet_text = "- " + entry
            wrapped_lines = self._wrap_text_to_lines(bullet_text, self.font_desc, text_max_width)
            all_entry_lines.extend(wrapped_lines)
            all_entry_lines.append("")

        max_entries_scroll = max(0, len(all_entry_lines) - self.max_entry_lines)
        self.entries_scroll_offset = max(0, min(self.entries_scroll_offset, max_entries_scroll))

        visible_entry_lines = all_entry_lines[
            self.entries_scroll_offset: self.entries_scroll_offset + self.max_entry_lines]

        for line in visible_entry_lines:
            if line:
                screen.blit(self.font_desc.render(line, True, COLOR_TEXT_MAIN), (details_x, current_y))
            current_y += self.font_desc.get_height()

        # 3. Draw Entry Scroll Indicators (Icons)
        if max_entries_scroll > 0 and self.focus == "details":
            icon_x = details_x + text_max_width - 30
            if self.entries_scroll_offset > 0:
                if self.icon_scroll_up:
                    screen.blit(self.icon_scroll_up, (icon_x, panel_y + 140))
                else:
                    screen.blit(self.font_ui.render(STRING_DIALOGUE_SCROLL_UP, True, COLOR_TEXT_HELPER),
                                (icon_x - 50, panel_y + 140))

            if self.entries_scroll_offset < max_entries_scroll:
                if self.icon_scroll_down:
                    screen.blit(self.icon_scroll_down, (icon_x, panel_y + panel_height - 25))
                else:
                    screen.blit(self.font_ui.render(STRING_DIALOGUE_SCROLL_DOWN, True, COLOR_TEXT_HELPER),
                                (icon_x - 50, panel_y + panel_height - 25))

        # Bottom UI hint
        if self.quests:
            hint_str = STRING_RETURN_PROMPT if self.focus == "details" else STRING_JOURNAL_READ_PROMPT
            hint_surf = self.font_ui.render(hint_str, True, COLOR_TEXT_HELPER)
            screen.blit(hint_surf, ((WINDOW_WIDTH - hint_surf.get_width()) // 2, panel_y + panel_height + 10))
