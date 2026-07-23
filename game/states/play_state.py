import pygame
import logging
from game.core.state import BaseState
from game.core.settings import KEY_PAUSE, KEY_TOGGLE_FULLSCREEN, KEY_INTERACT
from game.world.level import Level
from game.world.camera import Camera
from game.entities.player import Player
from game.entities.npc import NPC

log = logging.getLogger(__name__)

class PlayState(BaseState):
    def __init__(self, state_machine, level_filename: str, player_instance: Player, previous_level_name: str = ""):
        super().__init__(state_machine)
        self.level_filename = level_filename
        self.previous_level_name = previous_level_name
        self.player = player_instance

        # Load world map
        self.level = Level(self.level_filename)

        # Set player position
        spawn_x, spawn_y = self.level.get_spawn_position(self.previous_level_name)
        self.player.x = spawn_x
        self.player.y = spawn_y

        # Create NPC objects read from npc_spawn rectangles
        self.npcs: list[NPC] = []
        for spawn_info in self.level.npc_spawns:
            npc = NPC(
                x=spawn_info["x"],
                y=spawn_info["y"],
                npc_id=spawn_info["npc_id"],
                width=spawn_info["width"],
                height=spawn_info["height"]
            )
            self.npcs.append(npc)
            log.info(f"Spawned NPC '{npc.npc_id}' at ({npc.x}, {npc.y})")

        # Create camera bound to level dimensions
        self.camera = Camera(self.level.width, self.level.height)

        # Debug collision rendering flag
        self.debug_mode = False

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Interaction
                if event.key in KEY_INTERACT:
                    self._check_npc_interaction()

                # Pause menu trigger
                elif event.key in KEY_PAUSE:
                    log.info("Pause key pressed.")
                    # In future: self.state_machine.push(PauseState(self.state_machine))

                # Fullscreen toggle (F4)
                elif event.key in KEY_TOGGLE_FULLSCREEN:
                    pygame.display.toggle_fullscreen()
                    log.info("Toggled fullscreen mode.")

                # Debug mode toggle (F3)
                elif event.key == pygame.K_F3:
                    self.debug_mode = not self.debug_mode
                    log.debug(f"Debug Mode set to: {self.debug_mode}")

    def _check_npc_interaction(self):
        """Checks if the player tries to interact with a nearby NPC."""
        for npc in self.npcs:
            if npc.is_player_in_range(self.player.hitbox):
                log.info(f"Interacted with NPC: '{npc.npc_id}'!")
                # HERE, in the future, opening dialogue window will be called
                return

    def update(self, dt: float):
        # Combine static level colliders with dynamic NPC hitboxes
        active_colliders = self.level.collision_rects + [npc.hitbox for npc in self.npcs]

        # Update player position & collision against all objects
        self.player.update(dt, active_colliders)

        # Update NPCs
        for npc in self.npcs:
            npc.update(dt)

        # Update camera position
        self.camera.update(self.player.x, self.player.y, self.player.width, self.player.height)

        # Check level triggers (transition to another level)
        target_level = self.level.check_level_triggers(self.player.hitbox)
        if target_level:
            # Append .tmx extension if missing
            if not target_level.endswith(".tmx"):
                target_level += ".tmx"

            log.info(f"Player triggered transition to level: {target_level}")

            # Switch state to the new level, passing current level as previous_level_name
            new_play_state = PlayState(
                self.state_machine,
                level_filename=target_level,
                player_instance=self.player,
                previous_level_name=self.level_filename
            )
            self.state_machine.change(new_play_state)

    def draw(self, screen: pygame.Surface):
        screen.fill((0, 0, 0))

        # 1. Render map tile layers
        self.level.draw_tile_layers(screen, self.camera.x, self.camera.y)

        # 2. Render Y-sorted objects + player + npcs
        all_entities = [self.player] + self.npcs
        self.level.draw_sorted_objects(screen, self.camera.x, self.camera.y, all_entities)

        # 3. Optional Debug overlays
        if self.debug_mode:
            # Draw player hitbox in red
            p_hitbox = self.player.hitbox
            pygame.draw.rect(
                screen, (255, 0, 0),
                (p_hitbox.x - self.camera.x, p_hitbox.y - self.camera.y, p_hitbox.width, p_hitbox.height),
                2
            )
            # Draw map collision rects in green
            for rect in self.level.collision_rects:
                pygame.draw.rect(
                    screen, (0, 255, 0),
                    (rect.x - self.camera.x, rect.y - self.camera.y, rect.width, rect.height),
                    2
                )
            # NPCs' hitboxes and interaction radii (Blue / Yellow)
            for npc in self.npcs:
                # NPC collision
                pygame.draw.rect(
                    screen, (0, 0, 255),
                    (npc.x - self.camera.x, npc.y - self.camera.y, npc.width, npc.height),
                    2
                )
                # Interaction radius
                i_rect = npc.interaction_rect
                pygame.draw.rect(
                    screen, (255, 255, 0),
                    (i_rect.x - self.camera.x, i_rect.y - self.camera.y, i_rect.width, i_rect.height),
                    1
                )
