import pygame
import logging
import os
from game.entities.entity import Entity
from game.core.settings import IMAGES_DIR, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT

log = logging.getLogger(__name__)

class Player(Entity):
    DIRECTION_DOWN = 0
    DIRECTION_LEFT = 1
    DIRECTION_RIGHT = 2
    DIRECTION_UP = 3

    def __init__(self, x: float, y: float, initial_direction: int = DIRECTION_DOWN):
        # Initialize the base Entity class with coordinates
        super().__init__(x, y)

        # Stats
        self.speed = 220.0

        # Animation & Direction
        self.current_direction = initial_direction

        # Animation control
        self.animation_speed = 0.1125
        self.animation_timer = 0.0

        # Walking animation sequence
        self.walk_sequence = [0, 1, 2, 1]
        self.sequence_index = 1  # Start at "standing still" sprite
        self.animation_frame = self.walk_sequence[self.sequence_index]

        self.was_moving = False
        self.frames = self._load_spritesheet()

    def _load_spritesheet(self) -> list[list[pygame.Surface]]:
        """Loads the Actor1.png spritesheet and extracts player frames."""
        path = os.path.join(IMAGES_DIR, "characters", "Actor1.png")

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
                    pygame.Rect(
                        col * self.width,
                        row * self.height,
                        self.width,
                        self.height
                    )
                )
                row_frames.append(frame)
            frames.append(row_frames)

        return frames

    @property
    def current_sprite(self) -> pygame.Surface:
        """Returns the current image frame based on direction and animation state."""
        return self.frames[self.current_direction][self.animation_frame]

    def update(self, dt: float, collision_rects: list[pygame.Rect]):
        """Handles input, movement, sliding collision, and animation timing."""
        keys = pygame.key.get_pressed()
        move_input = pygame.math.Vector2(0, 0)

        # Read keys using settings mappings
        if any(keys[k] for k in KEY_LEFT): move_input.x -= 1
        if any(keys[k] for k in KEY_RIGHT): move_input.x += 1
        if any(keys[k] for k in KEY_UP): move_input.y -= 1
        if any(keys[k] for k in KEY_DOWN): move_input.y += 1

        is_trying_to_move = move_input.length() > 0

        if is_trying_to_move:
            move_input = move_input.normalize()

            # Update direction even if blocked by a wall
            if abs(move_input.x) > abs(move_input.y):
                self.current_direction = self.DIRECTION_RIGHT if move_input.x > 0 else self.DIRECTION_LEFT
            else:
                self.current_direction = self.DIRECTION_DOWN if move_input.y > 0 else self.DIRECTION_UP

            # Store position before attempting to move
            old_x = self.x
            old_y = self.y

            dx = move_input.x * self.speed * dt
            dy = move_input.y * self.speed * dt
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
        # Move X
        self.x += dx
        current_hitbox = self.hitbox
        for rect in colliders:
            if current_hitbox.colliderect(rect):
                if dx > 0:  # Moving right
                    self.x = rect.left - self.hitbox_width - self.hitbox_offset_x
                elif dx < 0:  # Moving left
                    self.x = rect.right - self.hitbox_offset_x
                break

        # Move Y
        self.y += dy
        current_hitbox = self.hitbox
        for rect in colliders:
            if current_hitbox.colliderect(rect):
                if dy > 0:  # Moving down
                    self.y = rect.top - self.height
                elif dy < 0:  # Moving up
                    self.y = rect.bottom - self.hitbox_offset_y
                break
