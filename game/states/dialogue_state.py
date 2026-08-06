import pygame
import logging
from game.core.state import BaseState
from game.entities.npc import NPC
from game.entities.player import Player
from game.entities.npc_data import NPC_DATA
from game.ui.dialogue_box import DialogueBox
from game.core.settings import KEY_INTERACT, KEY_UP, KEY_DOWN, KEY_PAUSE, KEY_RETURN, STRING_DIALOGUE_NO_REPLY_NPC
from game.llm.prompts import LLM_SYSTEM_BASE_CONTEXT, LORE
from game.llm.tool_calling import execute_tool_calls

log = logging.getLogger(__name__)

class DialogueState(BaseState):
    PHASE_PLAYER_TYPING = 0
    PHASE_WAITING = 1
    PHASE_NPC_REPLY = 2

    def __init__(self, state_machine, play_state, npc: NPC, player: Player, game_state):
        super().__init__(state_machine)
        self.play_state = play_state
        self.npc = npc
        self.player = player
        self.game_state = game_state

        self.current_phase = self.PHASE_PLAYER_TYPING
        self.player_text = ""
        self.npc_text = ""
        self.max_chars = 300
        self.scroll_offset = 0

        self.waiting_timer = 0.0
        self.dot_count = 0

        # LLM integration variables
        self.groq_client = self.game_state.groq_client  # retrieve previously initialized Groq client
        self.pending_response = None
        self.pending_error = None
        self.pending_tools = []  # list to hold parsed tool calls

        self.dialogue_box = DialogueBox()
        self.npc_face = self.dialogue_box.load_face(self.npc.face_filename, self.npc.face_index)

        player_config = NPC_DATA.get("player", {})
        p_face_file = player_config.get("face_file", "Actor1.png")
        p_face_idx = player_config.get("face_index", 0)
        self.player_face = self.dialogue_box.load_face(p_face_file, p_face_idx)
        self.player_name = player_config.get("name", "You")

        pygame.key.set_repeat(300, 50)

    def exit(self):
        pygame.key.set_repeat(0, 0)
        self.npc.reset_direction()

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.current_phase == self.PHASE_PLAYER_TYPING:
                    if event.key in KEY_PAUSE:
                        self.state_machine.pop()
                        return
                    elif event.key == pygame.K_RETURN:  # hardcoded ENTER
                        if 0 < len(self.player_text.strip()) <= self.max_chars:
                            self._send_message()
                    elif event.key == pygame.K_BACKSPACE:  # hardcoded BACKSPACE
                        self.player_text = self.player_text[:-1]

                elif self.current_phase == self.PHASE_NPC_REPLY:
                    if event.key in KEY_RETURN:
                        self.state_machine.pop()
                        return
                    elif event.key in KEY_INTERACT:
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
        self.scroll_offset = 0

        # 1. Fetch static NPC data
        npc_config = NPC_DATA.get(self.npc.npc_id, {})
        persona = npc_config.get("persona", "You are an NPC.")

        # 2. Fetch appropriate location Lore
        location = npc_config.get("location", "crowns_reach")
        location_lore = LORE.get(location, "")

        # 3. Gather LIVE SYSTEM DATA (Inventory, Journal, Stagnant State)
        inv_str = self.player.inventory.get_llm_string()
        journal_str = self.player.journal.get_llm_string()
        stagnant_state = self.game_state.get_stagnant_state(self.npc.npc_id)

        live_data = (
            "[LIVE SYSTEM DATA]\n"
            f"Player's Inventory: {inv_str}\n"
            f"Player's Journal:\n{journal_str}\n"
            f"Your current internal thought/relationship with the player: {stagnant_state}\n"
        )

        # 4. Build the final dynamic System Prompt
        system_content = f"{LLM_SYSTEM_BASE_CONTEXT}\n\n{location_lore}\n\n{persona}\n\n{live_data}"

        # 5. Build the messages payload for the LLM
        # Start with the system prompt, then add all previous conversation history
        messages = [{"role": "system", "content": system_content}]
        messages.extend(self.game_state.get_npc_history(self.npc.npc_id))
        messages.append({"role": "user", "content": self.player_text})

        # 6. Add player's message to persistent history immediately
        self.game_state.add_dialogue_message(self.npc.npc_id, "user", self.player_text)
        log.info(f"Sent message: {self.player_text} ({len(self.player_text)})")

        # 7. Trigger the background API call
        self.groq_client.generate_response_async(messages, self._on_api_response)

    def _on_api_response(self, text: str | None, parsed_tools: list[dict] | None, error: str | None):
        """
        Callback executed from the background thread once the HTTP request finishes.
        """
        if error:
            self.pending_error = error
        else:
            self.pending_response = text
            self.pending_tools = parsed_tools or []  # save tools

    def update(self, dt: float):
        if self.current_phase == self.PHASE_WAITING:
            # Dot animation logic
            self.waiting_timer += dt
            cycle = int(self.waiting_timer) % 5
            self.dot_count = cycle if cycle < 3 else 3

            # Check if the background thread has delivered a response or tools
            if self.pending_response is not None or self.pending_tools:

                # 1. Execute tools first, pushing HUD notifications
                if self.pending_tools:
                    execute_tool_calls(
                        tools=self.pending_tools,
                        play_state=self.play_state,
                        game_state=self.game_state,
                        current_npc_id=self.npc.npc_id  # <-- FIXED ARGUMENT NAME HERE
                    )
                    self.pending_tools = []

                # 2. Handle the text response
                if self.pending_response is not None:
                    # Edge case: LLM purely called a tool and returned an empty text string
                    if self.pending_response.strip() == "":
                        self._receive_message(STRING_DIALOGUE_NO_REPLY_NPC)
                    else:
                        self._receive_message(self.pending_response)

                    self.pending_response = None

            elif self.pending_error is not None:
                self._receive_message(f"[API ERROR] {self.pending_error}")
                self.pending_error = None

        self.play_state.hud.update(dt)  # Animate HUD notifications

    def _clean_llm_text(self, text: str) -> str:
        """
        Replaces fancy typography characters generated by the LLM
        with standard ASCII characters supported by pixel art fonts,
        and safely removes characters that cause Pygame rendering crashes.
        """
        # 1. Remove null characters that cause Pygame ValueError crashes
        text = text.replace('\x00', '')

        # 2. Replace non-breaking spaces (often rendered as crossed-out rectangles) with regular spaces
        text = text.replace('\xa0', ' ')

        replacements = {
            '“': '"',
            '”': '"',
            '‘': "'",
            '’': "'",
            '—': '-',
            '–': '-',
            '‑': '-',
            '…': '...',
            'ç': 'c',
        }
        for fancy_char, normal_char in replacements.items():
            text = text.replace(fancy_char, normal_char)

        # 3. Strip any trailing whitespace or invisible formatting characters at the end
        return text.strip()

    def _receive_message(self, text: str):
        cleaned_text = self._clean_llm_text(text)  # clean the text before displaying and saving it

        self.npc_text = cleaned_text
        self.current_phase = self.PHASE_NPC_REPLY
        self.scroll_offset = 0

        # Add to history only if it's a valid response, not a networking error
        if not text.startswith("[API ERROR]"):
            self.game_state.add_dialogue_message(self.npc.npc_id, "assistant", self.npc_text)

        log.info(f"Received reply: {self.npc_text}")

    def draw(self, screen: pygame.Surface):
        # 1. Draw the game world underneath
        self.play_state.draw(screen)

        # 2. Draw UI via DialogueBox component and update scroll limits
        max_scroll = self.dialogue_box.draw(
            screen=screen,
            current_phase=self.current_phase,
            npc_name=self.npc.display_name,
            player_name=self.player_name,
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

        # # Draw active notifications ON TOP of the dialogue box
        # self.play_state.hud.draw_notifications(screen)
