import os
import pygame
import logging
from game.core.settings import (
    IMAGES_DIR, FONT_DIALOGUE, FONT_UI, COLOR_MISSING,
    STRING_DIALOGUE_EMPTY, STRING_DIALOGUE_CONFIRM, STRING_DIALOGUE_WAIT,
    STRING_DIALOGUE_REPLY, STRING_DIALOGUE_TOO_MANY,
    STRING_DIALOGUE_SCROLL_UP, STRING_DIALOGUE_SCROLL_DOWN,
    COLOR_UI_BG_ALPHA, COLOR_UI_BOX_ALPHA, COLOR_TEXT_MAIN,
    COLOR_TEXT_HELPER, COLOR_TEXT_WARNING, COLOR_PREFIX_PLAYER,
    COLOR_PREFIX_NPC, COLOR_PREFIX_THINKING
)

log = logging.getLogger(__name__)


class DialogueBox:
    def __init__(self):
        self.font_dialogue = pygame.font.Font(*FONT_DIALOGUE)
        self.font_ui = pygame.font.Font(*FONT_UI)

        self.icon_scroll_up = self._load_icon("scroll_up.png")
        self.icon_scroll_down = self._load_icon("scroll_down.png")

    def _load_icon(self, filename: str) -> pygame.Surface | None:
        """Loads optional scroll arrow icons from assets/images/ui/"""
        path = os.path.join(IMAGES_DIR, "ui", filename)
        if os.path.exists(path):
            return pygame.image.load(path).convert_alpha()
        return None

    def load_face(self, filename: str, index: int) -> pygame.Surface:
        """Loads a 144x144 face from the faces directory (4 columns, 2 rows grid)."""
        fallback = pygame.Surface((144, 144))
        fallback.fill(COLOR_MISSING)

        if not filename:
            return fallback

        path = os.path.join(IMAGES_DIR, "characters", "faces", filename)
        try:
            faces_sheet = pygame.image.load(path).convert_alpha()
        except FileNotFoundError:
            log.warning(f"Face sheet '{filename}' not found at {path}. Using fallback.")
            return fallback

        col = index % 4
        row = index // 4
        return faces_sheet.subsurface(pygame.Rect(col * 144, row * 144, 144, 144))

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int, first_line_offset: int = 0) -> list[str]:
        lines = []
        # First, split the text by explicit newlines from the LLM
        paragraphs = text.split('\n')

        current_offset = first_line_offset

        for paragraph in paragraphs:
            # Preserve intentional empty lines (e.g., from "\n\n")
            if not paragraph:
                lines.append("")
                current_offset = 0  # reset offset on new lines
                continue

            words = paragraph.split(' ')
            current_line = []

            for word in words:
                test_line = ' '.join(current_line + [word])
                if font.size(test_line)[0] + current_offset <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
                    current_offset = 0  # prefix only affects the very first line

            if current_line:
                lines.append(' '.join(current_line))
            current_offset = 0  # reset offset for the next paragraph

        return lines

    def draw(
            self,
            screen: pygame.Surface,
            current_phase: int,
            npc_name: str,
            player_name: str,
            player_text: str,
            npc_text: str,
            dot_count: int,
            scroll_offset: int,
            player_face: pygame.Surface,
            npc_face: pygame.Surface,
            max_chars: int
    ) -> int:

        screen_width = screen.get_width()
        screen_height = screen.get_height()
        box_height = 240
        box_y = screen_height - box_height

        ui_surface = pygame.Surface((screen_width, box_height), pygame.SRCALPHA)
        ui_surface.fill(COLOR_UI_BG_ALPHA)

        text_area_width = screen_width - 144 - 60
        text_bg_rect = pygame.Rect(20, 20, text_area_width, box_height - 70)
        pygame.draw.rect(ui_surface, COLOR_UI_BOX_ALPHA, text_bg_rect, border_radius=8)

        face_bg_rect = pygame.Rect(screen_width - 144 - 20, 28, 144, 144)
        pygame.draw.rect(ui_surface, COLOR_UI_BOX_ALPHA, face_bg_rect, border_radius=8)

        screen.blit(ui_surface, (0, box_y))

        face_y = box_y + 28
        if current_phase == 0:
            screen.blit(player_face, (face_bg_rect.x, face_y))
        else:
            screen.blit(npc_face, (face_bg_rect.x, face_y))

        prefix_text = ""
        main_text = ""
        prefix_color = COLOR_PREFIX_PLAYER

        if current_phase == 0:
            prefix_text = f"{player_name}: "
            main_text = player_text
            if pygame.time.get_ticks() % 1000 < 500:
                main_text += "|"
            prefix_color = COLOR_PREFIX_PLAYER
        elif current_phase == 1:
            prefix_text = f"{npc_name} is thinking"
            main_text = "." * dot_count
            prefix_color = COLOR_PREFIX_THINKING
        elif current_phase == 2:
            prefix_text = f"{npc_name}: "
            main_text = npc_text
            prefix_color = COLOR_PREFIX_NPC

        prefix_surf = self.font_dialogue.render(prefix_text, True, prefix_color)
        prefix_width = prefix_surf.get_width()

        inner_text_rect = pygame.Rect(
            text_bg_rect.x + 15,
            box_y + text_bg_rect.y + 10,
            text_bg_rect.width - 30,
            text_bg_rect.height - 20
        )

        lines = self._wrap_text(main_text, self.font_dialogue, inner_text_rect.width, first_line_offset=prefix_width)

        line_height = self.font_dialogue.get_height() + 4
        max_lines_on_screen = inner_text_rect.height // line_height
        max_scroll = max(0, len(lines) - max_lines_on_screen)

        if current_phase == 0:
            effective_scroll = max_scroll
        else:
            effective_scroll = max(0, min(scroll_offset, max_scroll))

        visible_lines = lines[effective_scroll: effective_scroll + max_lines_on_screen]
        for i, line in enumerate(visible_lines):
            line_y = inner_text_rect.y + (i * line_height)

            if effective_scroll == 0 and i == 0:
                screen.blit(prefix_surf, (inner_text_rect.x, line_y))
                text_surf = self.font_dialogue.render(line, True, COLOR_TEXT_MAIN)
                screen.blit(text_surf, (inner_text_rect.x + prefix_width, line_y))
            else:
                text_surf = self.font_dialogue.render(line, True, COLOR_TEXT_MAIN)
                screen.blit(text_surf, (inner_text_rect.x, line_y))

        bottom_text = ""
        bottom_color = COLOR_TEXT_HELPER
        is_over_limit = len(player_text) > max_chars

        if is_over_limit and current_phase == 0:
            bottom_text = STRING_DIALOGUE_TOO_MANY
            bottom_color = COLOR_TEXT_WARNING
        else:
            if current_phase == 0:
                bottom_text = STRING_DIALOGUE_CONFIRM if len(player_text) > 0 else STRING_DIALOGUE_EMPTY
            elif current_phase == 1:
                bottom_text = STRING_DIALOGUE_WAIT
            elif current_phase == 2:
                bottom_text = STRING_DIALOGUE_REPLY

        bottom_surf = self.font_ui.render(bottom_text, True, bottom_color)
        helper_x = text_bg_rect.x + 15
        helper_y = box_y + text_bg_rect.bottom + 10
        screen.blit(bottom_surf, (helper_x, helper_y))

        if max_scroll > 0 and current_phase == 2:
            if effective_scroll < max_scroll:
                if self.icon_scroll_down:
                    screen.blit(self.icon_scroll_down, (inner_text_rect.right - 20, inner_text_rect.bottom - 20))
                else:
                    screen.blit(self.font_ui.render(STRING_DIALOGUE_SCROLL_DOWN, True, COLOR_TEXT_HELPER),
                                (helper_x + 350, helper_y))

            if effective_scroll > 0:
                if self.icon_scroll_up:
                    screen.blit(self.icon_scroll_up, (inner_text_rect.right - 20, inner_text_rect.top))
                else:
                    screen.blit(self.font_ui.render(STRING_DIALOGUE_SCROLL_UP, True, COLOR_TEXT_HELPER),
                                (helper_x + 500, helper_y))

        return max_scroll
