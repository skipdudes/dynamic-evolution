import pygame
import logging
from game.core.settings import IMAGES_DIR, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT

log = logging.getLogger(__name__)

class Player:
    DIRECTION_DOWN = 0
    DIRECTION_LEFT = 1
    DIRECTION_RIGHT = 2
    DIRECTION_UP = 3

    def __init__(self, x: float, y: float, initial_direction: int = DIRECTION_DOWN):
        self.x = x
        self.y = y

        # Dimensions
        self.width = 48
        self.height = 72

        # Hitbox dimensions and offsets
        self.hitbox_width = 36
        self.hitbox_height = 24
        self.hitbox_offset_x = (self.width - self.hitbox_width) // 2
        self.hitbox_offset_y = self.height - self.hitbox_height

        # Stats
        self.speed = 220.0  # 220.0

        # Animation & Direction
        self.current_direction = initial_direction

        # Animation control
        self.animation_speed = 0.1125  # 0.15
        self.animation_timer = 0.0

        # Walking animation sequence
        self.walk_sequence = [0, 1, 2, 1]
        self.sequence_index = 1  # By default, start at "standing still" sprite (idx 1)
        self.animation_frame = self.walk_sequence[self.sequence_index]

        self.was_moving = False
        self.frames = self._load_spritesheet()

    def _load_spritesheet(self) -> list[list[pygame.Surface]]:
        """
        Loads the Actor1.png spritesheet and extracts player frames.
        """
        import os
        path = os.path.join(IMAGES_DIR, "characters", "Actor1.png")

        try:
            spritesheet = pygame.image.load(path).convert_alpha()
        except FileNotFoundError:
            log.error(f"Spritesheet not found at: {path}")
            # Return an empty list or create a fallback surface if needed
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
    def hitbox(self) -> pygame.Rect:
        """
        Dynamically calculates current hitbox rect based on player position.
        """
        return pygame.Rect(
            int(self.x + self.hitbox_offset_x),
            int(self.y + self.hitbox_offset_y),
            self.hitbox_width,
            self.hitbox_height
        )

    @property
    def bottom(self) -> float:
        """
        Returns the true bottom Y coordinate, used for Y-sorting.
        """
        return self.y + self.height

    @property
    def current_sprite(self) -> pygame.Surface:
        """
        Returns the current image frame based on direction and animation state.
        """
        return self.frames[self.current_direction][self.animation_frame]

    def update(self, dt: float, collision_rects: list[pygame.Rect]):
        """
        Handles input, movement, sliding collision, and animation timing.
        """
        keys = pygame.key.get_pressed()

        # Vector2
        move_input = pygame.math.Vector2(0, 0)

        # Read keys using settings mappings
        if any(keys[k] for k in KEY_LEFT): move_input.x -= 1
        if any(keys[k] for k in KEY_RIGHT): move_input.x += 1
        if any(keys[k] for k in KEY_UP): move_input.y -= 1
        if any(keys[k] for k in KEY_DOWN): move_input.y += 1

        is_moving = move_input.length() > 0

        if is_moving:
            move_input = move_input.normalize()

            # Set animation direction
            if abs(move_input.x) > abs(move_input.y):
                self.current_direction = self.DIRECTION_RIGHT if move_input.x > 0 else self.DIRECTION_LEFT
            else:
                self.current_direction = self.DIRECTION_DOWN if move_input.y > 0 else self.DIRECTION_UP

            # Instant animation frame step when player starts moving (key tap responsiveness)
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
        else:
            # Reset to default standing pose when idle
            self.sequence_index = 1
            self.animation_frame = self.walk_sequence[self.sequence_index]
            self.animation_timer = 0.0

        self.was_moving = is_moving

        dx = move_input.x * self.speed * dt
        dy = move_input.y * self.speed * dt
        self._move_with_collision(dx, dy, collision_rects)

    def _move_with_collision(self, dx: float, dy: float, colliders: list[pygame.Rect]):
        """
        Applies movement and resolves overlaps along X and Y axes independently.
        """
        # Move X
        self.x += dx
        current_hitbox = self.hitbox
        for rect in colliders:
            if current_hitbox.colliderect(rect):
                if dx > 0:  # Moving right
                    self.x = rect.left - self.hitbox_width - self.hitbox_offset_x
                elif dx < 0:  # Moving left
                    self.x = rect.right - self.hitbox_offset_x
                break  # Sliding collision usually only needs one resolution per axis

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
