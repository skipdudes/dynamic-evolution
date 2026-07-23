import pygame
import logging
from game.core.state import BaseState
from game.entities.npc import NPC
from game.entities.player import Player

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
        self.max_chars = 150  # 300
        self.show_limit_warning = False

        # Font setup (using default pygame font for now)
        self.font = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        # Waiting animation variables
        self.waiting_timer = 0.0
        self.dot_count = 1

        # Dummy LLM response timer (to simulate waiting for API)
        self.dummy_api_timer = 0.0

        # Enable key repeat for natural backspace behavior
        pygame.key.set_repeat(300, 50)

    def exit(self):
        # Disable key repeat when leaving dialogue
        pygame.key.set_repeat(0, 0)

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state_machine.pop()
                    return

                if self.current_phase == self.PHASE_PLAYER_TYPING:
                    if event.key == pygame.K_RETURN:
                        if len(self.player_text.strip()) > 0:
                            self._send_message()
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_text = self.player_text[:-1]
                        self.show_limit_warning = False

                elif self.current_phase == self.PHASE_NPC_REPLY:
                    if event.key == pygame.K_RETURN:
                        # Reset for next turn
                        self.player_text = ""
                        self.current_phase = self.PHASE_PLAYER_TYPING

            # TEXTINPUT automatically handles shift, caps lock, and special characters
            elif event.type == pygame.TEXTINPUT:
                if self.current_phase == self.PHASE_PLAYER_TYPING:
                    if len(self.player_text) < self.max_chars:
                        self.player_text += event.text
                        self.show_limit_warning = False
                    else:
                        self.show_limit_warning = True

    def _send_message(self):
        """Transitions to waiting state and triggers API call."""
        self.current_phase = self.PHASE_WAITING
        self.waiting_timer = 0.0
        self.dummy_api_timer = 2.0  # Simulate a 2-second wait
        self.dot_count = 1
        log.info(f"Sent message to {self.npc.display_name}: {self.player_text}")

    def update(self, dt: float):
        if self.current_phase == self.PHASE_WAITING:
            # Animate thinking dots
            self.waiting_timer += dt
            if self.waiting_timer >= 0.5:
                self.waiting_timer = 0.0
                self.dot_count = (self.dot_count % 3) + 1

            # Simulate receiving response
            self.dummy_api_timer -= dt
            if self.dummy_api_timer <= 0:
                self._receive_message("This is a simulated response from the NPC. I heard what you said!")

    def _receive_message(self, text: str):
        self.npc_text = text
        self.current_phase = self.PHASE_NPC_REPLY
        log.info(f"Received reply from {self.npc.display_name}")

    def draw(self, screen: pygame.Surface):
        # 1. Draw the game world underneath
        self.play_state.draw(screen)

        # 2. Draw dialogue UI overlay
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        box_height = 200
        box_rect = pygame.Rect(0, screen_height - box_height, screen_width, box_height)

        # Main background box
        pygame.draw.rect(screen, (30, 30, 30), box_rect)
        pygame.draw.rect(screen, (200, 200, 200), box_rect, 3)  # Border

        # Helper text at the bottom
        bottom_text = "Press ESC to quit"
        if self.current_phase == self.PHASE_PLAYER_TYPING:
            if len(self.player_text) > 0:
                bottom_text = "Press ENTER to confirm, press ESC to quit"
            else:
                bottom_text = "Enter text. Press ESC to quit"
        elif self.current_phase == self.PHASE_WAITING:
            bottom_text = "Wait for the response"
        elif self.current_phase == self.PHASE_NPC_REPLY:
            bottom_text = "Press ENTER to reply, press ESC to quit"

        # Warning text for max characters
        if self.show_limit_warning and self.current_phase == self.PHASE_PLAYER_TYPING:
            warning_surf = self.font_small.render("Too many characters!", True, (255, 50, 50))
            screen.blit(warning_surf, (20, box_rect.top - 25))

        bottom_surf = self.font_small.render(bottom_text, True, (150, 150, 150))
        screen.blit(bottom_surf, (20, screen_height - 25))

        # Main text display area
        text_area_rect = pygame.Rect(20, box_rect.top + 20, screen_width - 200, box_height - 60)

        display_text = ""
        color = (255, 255, 255)

        if self.current_phase == self.PHASE_PLAYER_TYPING:
            display_text = self.player_text
            # Simple blinking cursor
            if pygame.time.get_ticks() % 1000 < 500:
                display_text += "|"
        elif self.current_phase == self.PHASE_WAITING:
            display_text = f"{self.npc.display_name} is thinking " + ("." * self.dot_count)
            color = (180, 180, 255)
        elif self.current_phase == self.PHASE_NPC_REPLY:
            display_text = self.npc_text
            color = (255, 215, 0)  # Gold for NPC text

        # Render main text
        text_surf = self.font.render(display_text, True, color)
        screen.blit(text_surf, (text_area_rect.x, text_area_rect.y))

        # Placeholder for NPC Face (144x144) on the right
        face_rect = pygame.Rect(screen_width - 164, box_rect.top + 28, 144, 144)
        pygame.draw.rect(screen, (100, 100, 100), face_rect)
        face_label = self.font_small.render("NPC FACE", True, (255, 255, 255))
        screen.blit(face_label, (face_rect.x + 35, face_rect.y + 60))

        # NPC Name above the face
        name_surf = self.font.render(self.npc.display_name, True, (255, 255, 255))
        screen.blit(name_surf, (face_rect.centerx - name_surf.get_width() // 2, face_rect.top - 30))
