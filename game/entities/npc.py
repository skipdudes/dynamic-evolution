import os
import pygame
import logging
from game.entities.entity import Entity
from game.core.settings import IMAGES_DIR
from game.entities.npc_data import NPC_DATA

log = logging.getLogger(__name__)

class NPC(Entity):
    # Constants for direction matching the spritesheet rows
    DIRECTION_DOWN = 0
    DIRECTION_LEFT = 1
    DIRECTION_RIGHT = 2
    DIRECTION_UP = 3

    # Dictionary to map string values from Tiled to our constants
    DIR_MAP = {
        "down": DIRECTION_DOWN,
        "left": DIRECTION_LEFT,
        "right": DIRECTION_RIGHT,
        "up": DIRECTION_UP
    }

    def __init__(self, x: float, y: float, npc_id: str, initial_direction: str = "down", width: int = 48, height: int = 72):
        super().__init__(x, y, width=width, height=height)
        self.npc_id: str = npc_id
        self.interaction_margin: int = 32

        # Safely convert the string from Tiled into a valid direction constant
        self.default_direction: int = self.DIR_MAP.get(initial_direction, self.DIRECTION_DOWN)
        self.current_direction: int = self.default_direction

        # Fetch NPC configuration based on ID, fallback if missing
        npc_config = NPC_DATA.get(self.npc_id, {})
        self.display_name: str = npc_config.get("name", "Unknown NPC")

        sprite_filename: str = npc_config.get("sprite_file", "")
        sprite_index: int = npc_config.get("sprite_index", 0)

        # Load face info (defaults to sprite info if not explicitly provided)
        self.face_filename: str = npc_config.get("face_file", sprite_filename)
        self.face_index: int = npc_config.get("face_index", sprite_index)

        # Load NPC standing frames for all 4 directions
        self.standing_frames = self._load_standing_frames(sprite_filename, sprite_index)

    def _load_standing_frames(self, filename: str, sprite_index: int) -> dict[int, pygame.Surface]:
        """
        Loads the 4 standing frames (Down, Left, Right, Up) for the NPC
        from an 8-character spritesheet.
        """
        if not filename:
            return self._create_fallback_sprites()

        path = os.path.join(IMAGES_DIR, "characters", filename)

        try:
            spritesheet = pygame.image.load(path).convert_alpha()
        except FileNotFoundError:
            log.warning(f"Spritesheet '{filename}' not found at path '{path}'. Using fallback sprite.")
            return self._create_fallback_sprites()

        # Calculate character block offset (4 columns, 2 rows in standard RPG sheets)
        char_col = sprite_index % 4
        char_row = sprite_index // 4

        base_x = char_col * (3 * self.width)
        base_y = char_row * (4 * self.height)

        frames = {}
        # Iterate over directions mapped to row offsets (0: Down, 1: Left, 2: Right, 3: Up)
        for direction, row_offset in enumerate([0, 1, 2, 3]):
            # The standing frame is always in the middle column (index 1) of the 3x4 block
            standing_x = base_x + (1 * self.width)
            standing_y = base_y + (row_offset * self.height)

            frames[direction] = spritesheet.subsurface(
                pygame.Rect(standing_x, standing_y, self.width, self.height)
            )

        return frames

    def _create_fallback_sprites(self) -> dict[int, pygame.Surface]:
        """Creates default colored rectangle surfaces if sprite loading fails."""
        fallback = pygame.Surface((self.width, self.height))
        fallback.fill((255, 215, 0))  # Gold placeholder

        # Return the same fallback surface for all 4 directions
        return {
            self.DIRECTION_DOWN: fallback,
            self.DIRECTION_LEFT: fallback,
            self.DIRECTION_RIGHT: fallback,
            self.DIRECTION_UP: fallback
        }

    @property
    def current_sprite(self) -> pygame.Surface:
        """Returns the current image frame based on the NPC's facing direction."""
        return self.standing_frames[self.current_direction]

    @property
    def interaction_rect(self) -> pygame.Rect:
        """Rectangle used for interaction between NPC and Player, based on the feet hitbox."""
        return self.hitbox.inflate(self.interaction_margin * 2, self.interaction_margin * 2)

    def is_player_in_range(self, player_hitbox: pygame.Rect) -> bool:
        """Checks if player is in range for interaction."""
        return self.interaction_rect.colliderect(player_hitbox)

    def turn_towards(self, target_rect: pygame.Rect):
        """
        Calculates the primary axis difference and makes the NPC face
        the center of the given target rectangle.
        """
        dx = target_rect.centerx - self.hitbox.centerx
        dy = target_rect.centery - self.hitbox.centery

        # Determine if the target is further along the X or Y axis
        if abs(dx) > abs(dy):
            self.current_direction = self.DIRECTION_RIGHT if dx > 0 else self.DIRECTION_LEFT
        else:
            self.current_direction = self.DIRECTION_DOWN if dy > 0 else self.DIRECTION_UP

    def reset_direction(self):
        """Resets the NPC's facing direction back to their initial map spawn state."""
        self.current_direction = self.default_direction

    def update(self, dt: float, *args, **kwargs):
        """NPC specific update logic."""
        pass
