import pygame
import logging
import os
from game.entities.entity import Entity
from game.entities.inventory import Inventory
from game.entities.journal import Journal
from game.core.settings import IMAGES_DIR, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT
from game.entities.npc_data import NPC_DATA

log = logging.getLogger(__name__)

class Player(Entity):
    DIRECTION_DOWN = 0
    DIRECTION_LEFT = 1
    DIRECTION_RIGHT = 2
    DIRECTION_UP = 3

    def __init__(self, x: float, y: float, initial_direction: int = DIRECTION_DOWN):
        super().__init__(x, y)

        # Stats
        self.speed = 220.0
        self.current_direction = initial_direction
        self.animation_speed = 0.1125
        self.animation_timer = 0.0
        self.inventory = Inventory()
        self.journal = Journal()

        # Walking animation sequence
        self.walk_sequence = [0, 1, 2, 1]
        self.sequence_index = 1  # Start at "standing still" sprite
        self.animation_frame = self.walk_sequence[self.sequence_index]

        self.was_moving = False
        self.input_vector = pygame.math.Vector2(0, 0)  # Input vector decoupled from update

        player_config = NPC_DATA.get("player", {})
        sprite_filename = player_config.get("sprite_file", "Actor1.png")
        self.frames = self._load_spritesheet(sprite_filename)

    def _load_spritesheet(self, filename: str) -> list[list[pygame.Surface]]:
        """Loads the player spritesheet and extracts player frames."""
        path = os.path.join(IMAGES_DIR, "characters", filename)

        try:
            spritesheet = pygame.image.load(path).convert_alpha()
        except FileNotFoundError:
            log.error(f"Spritesheet not found at: {path}")
            raise SystemExit(1)

        frames = []
        for row in range(4):
            row_frames = []
            for col in range(3):
                frame = spritesheet.subsurface(
                    pygame.Rect(col * self.width, row * self.height, self.width, self.height)
                )
                row_frames.append(frame)
            frames.append(row_frames)

        return frames

    @property
    def current_sprite(self) -> pygame.Surface:
        """Returns the current image frame based on direction and animation state."""
        return self.frames[self.current_direction][self.animation_frame]

    def handle_input(self, keys):
        """Processes continuous keyboard input and sets the input vector."""
        self.input_vector.x = 0
        self.input_vector.y = 0

        if any(keys[k] for k in KEY_LEFT): self.input_vector.x -= 1
        if any(keys[k] for k in KEY_RIGHT): self.input_vector.x += 1
        if any(keys[k] for k in KEY_UP): self.input_vector.y -= 1
        if any(keys[k] for k in KEY_DOWN): self.input_vector.y += 1

        if self.input_vector.length() > 0:
            self.input_vector = self.input_vector.normalize()

    def update(self, dt: float, collision_rects: list[pygame.Rect]):
        """Handles movement, sliding collision, and animation timing based on input_vector."""
        is_trying_to_move = self.input_vector.length() > 0

        if is_trying_to_move:
            # Update direction even if blocked by a wall
            if abs(self.input_vector.x) > abs(self.input_vector.y):
                self.current_direction = self.DIRECTION_RIGHT if self.input_vector.x > 0 else self.DIRECTION_LEFT
            else:
                self.current_direction = self.DIRECTION_DOWN if self.input_vector.y > 0 else self.DIRECTION_UP

            # Store position before attempting to move
            old_x = self.x
            old_y = self.y

            dx = self.input_vector.x * self.speed * dt
            dy = self.input_vector.y * self.speed * dt
            self._move_with_collision(dx, dy, collision_rects)

            # Check if player physically moved
            actually_moved = (abs(self.x - old_x) > 0.01) or (abs(self.y - old_y) > 0.01)

            if actually_moved:
                if not self.was_moving:
                    self.sequence_index = 0
                    self.animation_frame = self.walk_sequence[self.sequence_index]
                    self.animation_timer = 0.0
                else:
                    self.animation_timer += dt
                    if self.animation_timer >= self.animation_speed:
                        self.animation_timer = 0.0
                        self.sequence_index = (self.sequence_index + 1) % len(self.walk_sequence)
                        self.animation_frame = self.walk_sequence[self.sequence_index]
                self.was_moving = True
            else:
                self._reset_animation()
                self.was_moving = False
        else:
            self._reset_animation()
            self.was_moving = False

    def _reset_animation(self):
        """Helper to return player to default standing pose."""
        self.sequence_index = 1
        self.animation_frame = self.walk_sequence[self.sequence_index]
        self.animation_timer = 0.0

    def _move_with_collision(self, dx: float, dy: float, colliders: list[pygame.Rect]):
        """Applies movement and resolves overlaps along X and Y axes independently."""
        self.x += dx
        current_hitbox = self.hitbox
        for rect in colliders:
            if current_hitbox.colliderect(rect):
                if dx > 0:
                    self.x = rect.left - self.hitbox_width - self.hitbox_offset_x
                elif dx < 0:
                    self.x = rect.right - self.hitbox_offset_x
                break

        self.y += dy
        current_hitbox = self.hitbox
        for rect in colliders:
            if current_hitbox.colliderect(rect):
                if dy > 0:
                    self.y = rect.top - self.height
                elif dy < 0:
                    self.y = rect.bottom - self.hitbox_offset_y
                break

    def turn_towards(self, target_rect: pygame.Rect):
        """
        Calculates the primary axis difference and makes the player face
        the center of the given target rectangle.
        """
        dx = target_rect.centerx - self.hitbox.centerx
        dy = target_rect.centery - self.hitbox.centery

        # Determine if the target is further along the X or Y axis
        if abs(dx) > abs(dy):
            self.current_direction = self.DIRECTION_RIGHT if dx > 0 else self.DIRECTION_LEFT
        else:
            self.current_direction = self.DIRECTION_DOWN if dy > 0 else self.DIRECTION_UP

        # Ensure the player snaps to the idle standing animation for the new direction
        self._reset_animation()

    def stop(self):
        """
        Instantly halts player movement and resets the animation to idle.
        Useful for transitions, dialogues, and opening menus.
        """
        self.input_vector.x = 0
        self.input_vector.y = 0
        self._reset_animation()
        self.was_moving = False
        log.info("Stopped the player.")
