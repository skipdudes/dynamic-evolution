import pygame
import logging
from game.core.state import BaseState
from game.entities.npc import NPC
from game.entities.player import Player
from game.entities.npc_data import NPC_DATA
from game.ui.dialogue_box import DialogueBox
from game.core.settings import KEY_INTERACT, KEY_UP, KEY_DOWN, KEY_PAUSE

log = logging.getLogger(__name__)

class DialogueState(BaseState):
    PHASE_PLAYER_TYPING = 0
    PHASE_WAITING = 1
    PHASE_NPC_REPLY = 2

    def __init__(self, state_machine, play_state, npc: NPC, player: Player):
        super().__init__(state_machine)
        self.play_state = play_state
        self.npc = npc
        self.player = player

        self.current_phase = self.PHASE_PLAYER_TYPING
        self.player_text = ""
        self.npc_text = ""
        self.max_chars = 300
        self.scroll_offset = 0

        self.waiting_timer = 0.0
        self.dot_count = 0
        self.dummy_api_timer_const = 2
        self.dummy_api_timer = self.dummy_api_timer_const

        # Initialize Dialogue Box UI component
        self.dialogue_box = DialogueBox()

        # Load Faces using the UI component helper
        self.npc_face = self.dialogue_box.load_face(self.npc.face_filename, self.npc.face_index)

        player_config = NPC_DATA.get("player", {})
        p_face_file = player_config.get("face_file", "Actor1.png")
        p_face_idx = player_config.get("face_index", 0)
        self.player_face = self.dialogue_box.load_face(p_face_file, p_face_idx)

        pygame.key.set_repeat(300, 50)

    def exit(self):
        pygame.key.set_repeat(0, 0)

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_PAUSE:
                    if self.current_phase != self.PHASE_WAITING:
                        self.state_machine.pop()
                    return

                if self.current_phase == self.PHASE_PLAYER_TYPING:
                    if event.key == pygame.K_RETURN:
                        if 0 < len(self.player_text.strip()) <= self.max_chars:
                            self._send_message()
                    elif event.key == pygame.K_BACKSPACE:
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
                    if len(self.player_text) <= self.max_chars:
                        self.player_text += event.text

    def _send_message(self):
        self.current_phase = self.PHASE_WAITING
        self.waiting_timer = 0.0
        self.dummy_api_timer = self.dummy_api_timer_const
        self.scroll_offset = 0
        log.info(f"Sent message: {self.player_text} ({len(self.player_text)})")

    def update(self, dt: float):
        if self.current_phase == self.PHASE_WAITING:
            self.waiting_timer += dt
            cycle = int(self.waiting_timer) % 5
            self.dot_count = cycle if cycle < 3 else 3

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

    def draw(self, screen: pygame.Surface):
        # 1. Draw the game world underneath
        self.play_state.draw(screen)

        # 2. Draw UI via DialogueBox component and update scroll limits
        max_scroll = self.dialogue_box.draw(
            screen=screen,
            current_phase=self.current_phase,
            npc_name=self.npc.display_name,
            player_text=self.player_text,
            npc_text=self.npc_text,
            dot_count=self.dot_count,
            scroll_offset=self.scroll_offset,
            player_face=self.player_face,
            npc_face=self.npc_face,
            max_chars=self.max_chars
        )

        # Clamp state scroll offset safely
        if self.current_phase == self.PHASE_PLAYER_TYPING:
            self.scroll_offset = max_scroll
        else:
            self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
