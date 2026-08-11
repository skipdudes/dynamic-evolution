import pygame
import logging
from game.core.state import BaseState
from game.core.settings import (
    KEY_INTERACT, KEY_PAUSE, KEY_INVENTORY, KEY_JOURNAL,
    STRING_DIALOGUE_BEGIN_PROMPT, COLOR_NIGHT_FILTER, WINDOW_WIDTH, WINDOW_HEIGHT,
    STRING_NOTIFY_NEED_KEY, STRING_NOTIFY_MAGE_LOCK, STRING_NOTIFY_NO_TIME
)
from game.world.level import Level
from game.world.camera import Camera
from game.entities.player import Player
from game.entities.npc import NPC
from game.states.dialogue_state import DialogueState
from game.ui.hud import HUD

log = logging.getLogger(__name__)

class PlayState(BaseState):
    def __init__(self, state_machine, level_filename: str, player_instance: Player, game_state, previous_level_name: str = "", debug_mode: bool = False, hud=None, is_night: bool = False):
        super().__init__(state_machine)
        self.level_filename = level_filename
        self.previous_level_name = previous_level_name
        self.player = player_instance
        self.debug_mode = debug_mode
        self.game_state = game_state
        self.is_night = is_night

        # Load world map
        self.level = Level(self.level_filename)

        # Set player position
        spawn_x, spawn_y = self.level.get_spawn_position(self.previous_level_name)
        self.player.x = spawn_x
        self.player.y = spawn_y

        # Create NPC objects read from npc_spawn rectangles
        self.npcs: list[NPC] = []
        for spawn_info in self.level.npc_spawns:
            npc_id = spawn_info["npc_id"]
            spawn_id = spawn_info["spawn_id"]

            # Only instantiate and append the NPC if GameState confirms this is their active location
            if self.game_state.is_npc_spawn_active(npc_id, spawn_id):
                npc = NPC(
                    x=spawn_info["x"],
                    y=spawn_info["y"],
                    npc_id=npc_id,
                    initial_direction=spawn_info.get("direction", "down"),
                    width=spawn_info.get("width", 48),
                    height=spawn_info.get("height", 72)
                )
                self.npcs.append(npc)
                log.info(
                    f"Spawned NPC '{npc_id}' at location '{spawn_id}' facing {spawn_info.get('direction', 'down')}")
            else:
                log.debug(f"Skipped NPC '{npc_id}' at location '{spawn_id}' (Inactive state)")

        # Create camera bound to level dimensions
        self.camera = Camera(self.level.width, self.level.height)

        # Force initial camera update so it doesn't start at (0, 0)
        self.camera.update(self.player.x, self.player.y, self.player.width, self.player.height)

        # Interaction tracking
        self.active_prompt_npc: NPC | None = None
        self.recently_interacted_npc: NPC | None = None

        # Initialize HUD or use the existing one passed from the previous level
        if hud is None:
            self.hud = HUD()
        else:
            self.hud = hud

        self.pending_teleport: str | None = None  # variable to hold queued teleportations from LLM tools
        self.locked_door_spam_guard = False  # prevents HUD spam for locked doors
        self.pending_ending = None

        # Automatically start Quest 3 when the player first arrives in the meadow (after teleport)
        if self.level_filename == "meadow.tmx" and not self.player.journal.has_quest("quest_stranger_tarnstead"):
            self.player.journal.add_quest("quest_stranger_tarnstead")

            entry_text = (
                "The teleportation was successful. I am in a meadow somewhere in Tarnstead. "
                "I should head east into the settlement and find a local tavern. "
                "A bartender is always the best source of rumors."
            )
            self.player.journal.add_entry("quest_stranger_tarnstead", entry_text)

            # Show HUD notification immediately upon map load
            from game.entities.quest_data import QUESTS_DB
            from game.core.settings import STRING_NOTIFY_QUEST

            q_name = QUESTS_DB["quest_stranger_tarnstead"]["title"]
            self.hud.add_notification(f"{STRING_NOTIFY_QUEST}{q_name}")
            log.info("Environmental Trigger: Started 'A Stranger in Tarnstead'")

    def teleport_player(self, destination: str):
        """
        Queues a teleportation. The actual map transition will happen
        in the update loop once the dialogue state is popped.
        """
        self.pending_teleport = destination
        log.info(f"Teleport queued for: {destination}")

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_INTERACT:
                    self._check_npc_interaction()

                elif event.key in KEY_PAUSE:
                    self.player.stop()
                    from game.states.pause_state import PauseState
                    self.state_machine.push(PauseState(self.state_machine, self))
                    return

                elif event.key in KEY_INVENTORY:
                    self.player.stop()
                    from game.states.inventory_state import InventoryState
                    self.state_machine.push(InventoryState(self.state_machine, self))
                    return

                elif event.key in KEY_JOURNAL:
                    self.player.stop()
                    from game.states.journal_state import JournalState
                    self.state_machine.push(JournalState(self.state_machine, self))
                    return

    def handle_input(self, keys):
        """Passes continuous input state to the player."""
        self.player.handle_input(keys)

    def _check_npc_interaction(self):
        """Checks if the player tries to interact with a nearby NPC."""
        for npc in self.npcs:
            if npc.is_player_in_range(self.player.hitbox):
                log.info(f"Interacted with NPC: '{npc.npc_id}'!")
                self._start_dialogue(npc)
                return

    def _start_dialogue(self, npc: NPC):
        """Pushes the dialogue state onto the state machine stack."""
        log.info(f"Starting conversation with {npc.npc_id}")

        self.player.stop()  # halt the player completely before opening the dialogue box

        # Make the player and NPC turn to face each other
        self.player.turn_towards(npc.hitbox)
        npc.turn_towards(self.player.hitbox)

        self.recently_interacted_npc = npc
        self.active_prompt_npc = None

        dialogue_state = DialogueState(self.state_machine, self, npc, self.player, self.game_state)
        self.state_machine.push(dialogue_state)

    def update(self, dt: float):
        # --- ENDGAME HANDLING ---
        if getattr(self, "pending_ending", None):
            ending_type = self.pending_ending
            self.pending_ending = None  # Clear it

            log.info(f"Triggering game ending: {ending_type}")

            # Stop player
            self.player.stop()

            from game.states.story_board_state import StoryBoardState
            from game.states.main_menu_state import MainMenuState
            from game.core.settings import (
                STRING_EPILOGUE_GOOD_HEADER, STRING_EPILOGUE_GOOD_TEXT, COLOR_HEADER_EPILOGUE_GOOD,
                STRING_EPILOGUE_BAD_HEADER, STRING_EPILOGUE_BAD_TEXT, COLOR_HEADER_EPILOGUE_BAD
            )

            if ending_type == "good":
                header = STRING_EPILOGUE_GOOD_HEADER
                text = STRING_EPILOGUE_GOOD_TEXT
                color = COLOR_HEADER_EPILOGUE_GOOD
            else:
                header = STRING_EPILOGUE_BAD_HEADER
                text = STRING_EPILOGUE_BAD_TEXT
                color = COLOR_HEADER_EPILOGUE_BAD

            # After the ending text, return to the main menu
            next_state = MainMenuState(self.state_machine)

            outro = StoryBoardState(
                self.state_machine,
                header,
                text,
                next_state,
                title_color=color,
                hold_time=8.0
            )

            # Transition to Outro immediately
            from game.states.transition_state import TransitionState
            transition = TransitionState(
                self.state_machine,
                prev_state=self,
                next_state_func=lambda: outro,
                duration=1.0
            )
            self.state_machine.change(transition)
            return  # Halt any further update logic on this frame!

        # Combine static level colliders with dynamic NPC hitboxes
        active_colliders = self.level.collision_rects + [npc.hitbox for npc in self.npcs]

        # Player logic update uses the input gathered in handle_input
        self.player.update(dt, active_colliders)

        # Update NPCs
        for npc in self.npcs:
            npc.update(dt)

        # Update camera position
        self.camera.update(self.player.x, self.player.y, self.player.width, self.player.height)

        # Update HUD (timers for notifications)
        self.hud.update(dt)

        # Update interaction prompt logic
        npc_in_range = None
        for npc in self.npcs:
            if npc.is_player_in_range(self.player.hitbox):
                npc_in_range = npc
                break

        if npc_in_range:
            # If we are in range of the NPC we just talked to, keep prompt hidden
            if self.recently_interacted_npc == npc_in_range:
                self.active_prompt_npc = None
            else:
                self.active_prompt_npc = npc_in_range
        else:
            # Player walked away, clear the memory of recent interaction
            self.recently_interacted_npc = None
            self.active_prompt_npc = None

        # Check for queued teleports (from LLM) or physical level triggers
        target_level = None
        is_teleport = False

        if self.pending_teleport:
            target_level = self.pending_teleport
            self.pending_teleport = None  # Clear it so it doesn't trigger endlessly
            is_teleport = True
        else:
            target_level = self.level.check_level_triggers(self.player.hitbox)

            # --- CUSTOM LOCK LOGIC FOR TAVERN, MAGE HOUSE, AND FINALE ---
            if target_level:
                # Strip extensions for safe comparison
                check_name = target_level.replace(".tmx", "")
                current_name = getattr(self, "level_filename", "").replace(".tmx", "")

                # 1. Tavern Bedroom Lock
                if current_name == "tavern_rooms" and check_name == "tavern_bedroom":
                    if not self.player.inventory.has_item("tavern_key"):
                        target_level = None  # Block transition
                        if not getattr(self, "locked_door_spam_guard", False):
                            self.hud.add_notification(STRING_NOTIFY_NEED_KEY)
                            self.locked_door_spam_guard = True
                    else:
                        self.locked_door_spam_guard = False

                # 2. Mage House Lock (Quest 9: The Point of No Return)
                elif current_name == "house_mage" and check_name == "oldworld":
                    quest_9 = self.player.journal.quests.get("quest_point_no_return")
                    if quest_9 and quest_9.get("status") == "active":
                        target_level = None  # Block transition
                        if not getattr(self, "locked_door_spam_guard", False):
                            self.hud.add_notification(STRING_NOTIFY_MAGE_LOCK)
                            self.locked_door_spam_guard = True
                    else:
                        self.locked_door_spam_guard = False

                # 3. Finale Lock (Quest 10: Checkmate) - Block everything except castle
                elif current_name == "oldworld" and check_name in ["inn", "house_marquis", "house_mage"]:
                    quest_10 = self.player.journal.quests.get("quest_checkmate")
                    if quest_10 and quest_10.get("status") == "active":
                        target_level = None  # Block transition
                        if not getattr(self, "locked_door_spam_guard", False):
                            self.hud.add_notification(STRING_NOTIFY_NO_TIME)
                            self.locked_door_spam_guard = True
                    else:
                        self.locked_door_spam_guard = False
                else:
                    self.locked_door_spam_guard = False
            else:
                # Reset spam guard if player steps off the trigger
                self.locked_door_spam_guard = False

        if target_level:
            if not target_level.endswith(".tmx"):
                target_level += ".tmx"  # Append .tmx extension if missing

            log.info(f"Player triggered transition to level: {target_level}")
            check_name = target_level.replace(".tmx", "")

            # Stop the player completely on old level
            self.player.stop()

            # Define what to load in the background
            def load_next_level():
                next_play_state = PlayState(
                    self.state_machine,
                    level_filename=target_level,
                    player_instance=self.player,
                    game_state=self.game_state,
                    previous_level_name=self.level_filename,
                    debug_mode=self.debug_mode,
                    hud=self.hud,
                    is_night=self.is_night
                )

                # --- STORYBOARD INTERCEPTION (Mid-Game Crossroads) ---
                # Triggered ONLY if we teleport to house_mage and Quest 9 is active
                if is_teleport and check_name == "house_mage":
                    quest_9 = self.player.journal.quests.get("quest_point_no_return")
                    if quest_9 and quest_9.get("status") == "active":
                        from game.states.story_board_state import StoryBoardState
                        from game.core.settings import (
                            STRING_CROSSROADS_HEADER,
                            STRING_CROSSROADS_TEXT,
                            COLOR_HEADER_CROSSROADS
                        )
                        return StoryBoardState(
                            self.state_machine,
                            STRING_CROSSROADS_HEADER,
                            STRING_CROSSROADS_TEXT,
                            next_play_state,  # Passes the initialized PlayState to load after the storyboard!
                            title_color=COLOR_HEADER_CROSSROADS,
                            hold_time=6.0
                        )

                return next_play_state

            # Transition based on next_state_func
            from game.states.transition_state import TransitionState
            transition = TransitionState(
                self.state_machine,
                prev_state=self,
                next_state_func=load_next_level,
                duration=0.3
            )
            self.state_machine.change(transition)

    def draw(self, screen: pygame.Surface):
        screen.fill((0, 0, 0))

        # 1. Render map tile layers
        self.level.draw_tile_layers(screen, self.camera.x, self.camera.y)

        # 2. Render Y-sorted objects + player + npcs
        all_entities = [self.player] + self.npcs
        self.level.draw_sorted_objects(screen, self.camera.x, self.camera.y, all_entities)

        # 2.5 Draw Night Filter and Light Masks
        if self.is_night and self.level.level_type == 'outdoor':
            night_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            night_surf.fill(COLOR_NIGHT_FILTER)

            for light in self.level.lights:
                # Calculate screen position based on the camera
                screen_x = light["draw_x"] - self.camera.x
                screen_y = light["draw_y"] - self.camera.y

                mask_w = light["mask"].get_width()
                mask_h = light["mask"].get_height()

                # Optimization: render only if the mask is currently visible on the screen
                if -mask_w < screen_x < WINDOW_WIDTH and -mask_h < screen_y < WINDOW_HEIGHT:
                    # BLEND_RGBA_SUB subtracts the light mask's alpha from the night filter
                    night_surf.blit(light["mask"], (screen_x, screen_y), special_flags=pygame.BLEND_RGBA_SUB)

            screen.blit(night_surf, (0, 0))

        # 3. Draw Interaction Prompt via HUD
        if self.active_prompt_npc:
            prompt_text = f"{STRING_DIALOGUE_BEGIN_PROMPT}{self.active_prompt_npc.display_name}"
            self.hud.draw_interaction_prompt(screen, prompt_text)

        # 4. Draw active notifications
        self.hud.draw_notifications(screen)

        # 5. Optional Debug overlays
        if self.debug_mode:
            p_hitbox = self.player.hitbox
            pygame.draw.rect(screen, (255, 0, 0),  # red: player hitbox
                             (p_hitbox.x - self.camera.x, p_hitbox.y - self.camera.y, p_hitbox.width, p_hitbox.height),
                             2)
            for rect in self.level.collision_rects:
                pygame.draw.rect(screen, (0, 255, 0),  # green: map collision
                                 (rect.x - self.camera.x, rect.y - self.camera.y, rect.width, rect.height), 2)
            for npc in self.npcs:
                pygame.draw.rect(screen, (0, 0, 255),  # npc hitbox
                                 (npc.x - self.camera.x, npc.y - self.camera.y, npc.width, npc.height), 2)
                i_rect = npc.interaction_rect
                pygame.draw.rect(screen, (255, 255, 0),  # npc interaction range
                                 (i_rect.x - self.camera.x, i_rect.y - self.camera.y, i_rect.width, i_rect.height), 1)
