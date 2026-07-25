import os
import pygame
import logging
from game.core.state import BaseState
from game.entities.npc import NPC
from game.entities.player import Player
from game.entities.npc_data import NPC_DATA
from game.core.settings import KEY_INTERACT, KEY_UP, KEY_DOWN, KEY_PAUSE, IMAGES_DIR, FONT_DIALOGUE_PATH, FONT_DIALOGUE_SIZE, FONT_UI_PATH, FONT_UI_SIZE, COLOR_MISSING

log = logging.getLogger(__name__)

class DialogueState(BaseState):
    PHASE_PLAYER_TYPING = 0
    PHASE_WAITING = 1
    PHASE_NPC_REPLY = 2

    def __init__(self, state_machine, play_state, npc: NPC, player: Player):
        super().__init__(state_machine)
        self.play_state = play_state  # Reference to draw the background map
        self.npc = npc
        self.player = player

        self.current_phase = self.PHASE_PLAYER_TYPING
        self.player_text = ""
        self.npc_text = ""
        self.max_chars = 300

        self.scroll_offset = 0
        self.font = pygame.font.Font(FONT_DIALOGUE_PATH, FONT_DIALOGUE_SIZE) # Dialogue font (change `font` to `font_dialogue`)
        self.font_small = pygame.font.Font(FONT_UI_PATH, FONT_UI_SIZE) # UI font (change `font_small` to `font_ui`)

        self.waiting_timer = 0.0
        self.dot_count = 0
        self.dummy_api_timer_const = 2  # "20" to test the dot animation, to be removed later
        self.dummy_api_timer = self.dummy_api_timer_const  # to be removed later

        # Load Faces
        self.npc_face = self._load_face(self.npc.face_filename, self.npc.face_index)
        player_config = NPC_DATA.get("player", {})
        p_face_file = player_config.get("face_file", "Actor1.png")
        p_face_idx = player_config.get("face_index", 0)
        self.player_face = self._load_face(p_face_file, p_face_idx)

        pygame.key.set_repeat(300, 50)

    def _load_face(self, filename: str, index: int) -> pygame.Surface:
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
        face_x = col * 144
        face_y = row * 144

        return faces_sheet.subsurface(pygame.Rect(face_x, face_y, 144, 144))

    def exit(self):
        pygame.key.set_repeat(0, 0)

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_PAUSE:
                    if self.current_phase != self.PHASE_WAITING:  # Allow exit only if not waiting for API
                        self.state_machine.pop()
                    return

                if self.current_phase == self.PHASE_PLAYER_TYPING:
                    if event.key == pygame.K_RETURN:  # hardcoded, standard
                        if 0 < len(self.player_text.strip()) <= self.max_chars:  # send ONLY if within limits and not empty
                            self._send_message()
                    elif event.key == pygame.K_BACKSPACE:  # hardcoded, standard
                        self.player_text = self.player_text[:-1]

                elif self.current_phase == self.PHASE_NPC_REPLY:
                    if event.key in KEY_INTERACT:
                        self.player_text = ""
                        self.current_phase = self.PHASE_PLAYER_TYPING
                        self.scroll_offset = 0
                    elif event.key in KEY_UP:
                        self.scroll_offset -= 1
                    elif event.key in KEY_DOWN:
                        self.scroll_offset += 1

            elif event.type == pygame.TEXTINPUT:
                if self.current_phase == self.PHASE_PLAYER_TYPING:
                    # Allow input if current length is <= max_chars (can type 1 more over limit to see warning)
                    if len(self.player_text) <= self.max_chars:
                        self.player_text += event.text

    def _send_message(self):
        self.current_phase = self.PHASE_WAITING
        self.waiting_timer = 0.0
        self.dummy_api_timer = self.dummy_api_timer_const
        self.scroll_offset = 0
        # log.info(f"Sent message to {self.npc.display_name}")
        log.info(f"Sent message: {self.player_text} ({len(self.player_text)})")

    def update(self, dt: float):
        if self.current_phase == self.PHASE_WAITING:
            self.waiting_timer += dt

            cycle = int(self.waiting_timer) % 5
            if cycle == 0:
                self.dot_count = 0
            elif cycle == 1:
                self.dot_count = 1
            elif cycle == 2:
                self.dot_count = 2
            else:
                self.dot_count = 3

            self.dummy_api_timer -= dt
            if self.dummy_api_timer <= 0:
                dummy_long_text = (
                    "This is a simulated response from the NPC. I heard what you said! "
                    "Let me tell you a very long story to test the wrapping and scrolling system. "
                    "Once upon a time, there was a developer who made an awesome RPG in Python. "
                    "The system was robust, and the game loop was perfect. Is the text wrapping properly? "
                    "Use the UP and DOWN arrow keys to scroll through this message if it gets cut off!"
                )
                self._receive_message(dummy_long_text)

    def _receive_message(self, text: str):
        self.npc_text = text
        self.current_phase = self.PHASE_NPC_REPLY
        self.scroll_offset = 0
        log.info(f"Received reply from {self.npc.display_name}")

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> list[str]:
        """Splits a string into a list of strings (lines) that fit within max_width."""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def draw(self, screen: pygame.Surface):
        self.play_state.draw(screen)  # draw the game world underneath

        screen_width = screen.get_width()
        screen_height = screen.get_height()
        box_height = 200  # dialogue box
        box_y = screen_height - box_height

        ui_surface = pygame.Surface((screen_width, box_height), pygame.SRCALPHA)  # transparent surface for the UI background
        ui_surface.fill((0, 0, 0, 153))  # 60% opacity black (153/255)

        text_area_width = screen_width - 144 - 60  # text area background
        text_bg_rect = pygame.Rect(20, 20, text_area_width, box_height - 40)
        pygame.draw.rect(ui_surface, (0, 0, 0, 230), text_bg_rect, border_radius=8)  # 90% opacity black (230/255) with rounded corners

        face_bg_rect = pygame.Rect(screen_width - 144 - 20, 28, 144, 144)  # face area background
        pygame.draw.rect(ui_surface, (0, 0, 0, 230), face_bg_rect, border_radius=8)  # 90% opacity black

        screen.blit(ui_surface, (0, box_y))  # entire transparent UI surface onto the main screen

        face_y = box_y + 28  # draw faces
        if self.current_phase == self.PHASE_PLAYER_TYPING:
            screen.blit(self.player_face, (face_bg_rect.x, face_y))
        else:
            screen.blit(self.npc_face, (face_bg_rect.x, face_y))

        display_text = ""  # Main Text Content
        text_color = (255, 255, 255)

        if self.current_phase == self.PHASE_PLAYER_TYPING:
            display_text = "You: " + self.player_text
            if pygame.time.get_ticks() % 1000 < 500:  # Blinking cursor
                display_text += "|"
        elif self.current_phase == self.PHASE_WAITING:
            display_text = f"{self.npc.display_name} is thinking"
            display_text += "." * self.dot_count
        elif self.current_phase == self.PHASE_NPC_REPLY:
            display_text = f"{self.npc.display_name}: " + self.npc_text

        inner_text_rect = pygame.Rect(text_bg_rect.x + 15, box_y + text_bg_rect.y + 10, text_bg_rect.width - 30,
                                      text_bg_rect.height - 20)
        lines = self._wrap_text(display_text, self.font, inner_text_rect.width)  # text wrapping & scrolling

        line_height = self.font.get_height() + 4
        max_lines_on_screen = inner_text_rect.height // line_height
        max_scroll = max(0, len(lines) - max_lines_on_screen)

        if self.current_phase == self.PHASE_PLAYER_TYPING:
            self.scroll_offset = max_scroll
        else:
            self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

        visible_lines = lines[self.scroll_offset: self.scroll_offset + max_lines_on_screen]
        for i, line in enumerate(visible_lines):
            text_surf = self.font.render(line, True, text_color)
            screen.blit(text_surf, (inner_text_rect.x, inner_text_rect.y + (i * line_height)))

        bottom_text = ""  # helper prompts
        bottom_color = (128, 128, 128)
        is_over_limit = len(self.player_text) > self.max_chars

        if is_over_limit and self.current_phase == self.PHASE_PLAYER_TYPING:
            bottom_text = "Too many characters!"
            bottom_color = (255, 0, 0)
        else:
            if self.current_phase == self.PHASE_PLAYER_TYPING:
                if len(self.player_text) > 0:
                    bottom_text = "Press ENTER to confirm, press ESC to quit"
                else:
                    bottom_text = "Enter text. Press ESC to quit"
            elif self.current_phase == self.PHASE_WAITING:
                bottom_text = "Wait for the response"
            elif self.current_phase == self.PHASE_NPC_REPLY:
                bottom_text = "Press ENTER to reply, press ESC to quit"

        if max_scroll > 0 and self.current_phase == self.PHASE_NPC_REPLY:  # scroll indicators for NPC reply
            if self.scroll_offset < max_scroll:
                bottom_text += "  [v Scroll Down]"
            if self.scroll_offset > 0:
                bottom_text += "  [^ Scroll Up]"

        bottom_surf = self.font_small.render(bottom_text, True, bottom_color)
        helper_x = text_bg_rect.x + 15  # helper text pos
        helper_y = box_y + text_bg_rect.bottom + 5
        screen.blit(bottom_surf, (helper_x, helper_y))
