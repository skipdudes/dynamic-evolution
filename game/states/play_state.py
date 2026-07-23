import pygame
import logging
from game.core.state import BaseState
from game.core.settings import KEY_PAUSE, KEY_TOGGLE_FULLSCREEN
from game.world.level import Level
from game.world.camera import Camera
from game.entities.player import Player

log = logging.getLogger(__name__)

class PlayState(BaseState):
    def __init__(self, state_machine, level_filename: str, player_instance: Player, previous_level_name: str = ""):
        super().__init__(state_machine)
        self.level_filename = level_filename
        self.previous_level_name = previous_level_name
        self.player = player_instance

        # Load world map
        self.level = Level(self.level_filename)

        # Calculate spawn position based on previous level
        spawn_x, spawn_y = self.level.get_spawn_position(self.previous_level_name)

        # Update the existing player's position
        self.player.x = spawn_x
        self.player.y = spawn_y

        # Create camera bound to level dimensions
        self.camera = Camera(self.level.width, self.level.height)

        # Debug collision rendering flag
        self.debug_mode = False

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Pause menu trigger
                if event.key in KEY_PAUSE:
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

    def update(self, dt: float):
        # Update player position & collision
        self.player.update(dt, self.level.collision_rects)

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

        # 2. Render Y-sorted objects + player
        self.level.draw_sorted_objects(screen, self.camera.x, self.camera.y, self.player)

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
