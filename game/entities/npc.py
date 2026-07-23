import os
import pygame
import logging
from game.entities.entity import Entity
from game.core.settings import IMAGES_DIR
from game.entities.npc_data import NPC_DATA

log = logging.getLogger(__name__)

class NPC(Entity):
    def __init__(self, x: float, y: float, npc_id: str, width: int = 48, height: int = 72):
        super().__init__(x, y, width=width, height=height)
        self.npc_id: str = npc_id
        self.interaction_margin: int = 32

        # Fetch NPC configuration based on ID, fallback if missing
        npc_config = NPC_DATA.get(self.npc_id, {})
        self.display_name: str = npc_config.get("name", "Unknown NPC")

        sprite_filename: str = npc_config.get("sprite_file", "")
        sprite_index: int = npc_config.get("sprite_index", 0)

        # Load face info (defaults to sprite info if not explicitly provided)
        self.face_filename: str = npc_config.get("face_file", sprite_filename)
        self.face_index: int = npc_config.get("face_index", sprite_index)

        # Load NPC sprite surface
        self.current_sprite = self._load_sprite(sprite_filename, sprite_index)

    def _load_sprite(self, filename: str, sprite_index: int) -> pygame.Surface:
        """
        Loads a single standing frame for the NPC from an 8-character spritesheet.
        Grid layout:
        0 1 2 3
        4 5 6 7
        """
        if not filename:
            return self._create_fallback_sprite()

        path = os.path.join(IMAGES_DIR, "characters", filename)

        try:
            spritesheet = pygame.image.load(path).convert_alpha()
        except FileNotFoundError:
            log.warning(f"Spritesheet '{filename}' not found at path '{path}'. Using fallback sprite.")
            return self._create_fallback_sprite()

        # Calculate character block offset (4 columns, 2 rows)
        char_col = sprite_index % 4
        char_row = sprite_index // 4

        base_x = char_col * (3 * self.width)
        base_y = char_row * (4 * self.height)

        # Standing pose facing down: column index 1, row index 0
        standing_x = base_x + (1 * self.width)
        standing_y = base_y + (0 * self.height)

        return spritesheet.subsurface(
            pygame.Rect(standing_x, standing_y, self.width, self.height)
        )

    def _create_fallback_sprite(self) -> pygame.Surface:
        """Creates a default colored rectangle surface if sprite loading fails."""
        fallback = pygame.Surface((self.width, self.height))
        fallback.fill((255, 215, 0))  # Gold placeholder
        return fallback

    @property
    def interaction_rect(self) -> pygame.Rect:
        """Rectangle used for interaction between NPC and Player, based on the feet hitbox."""
        return self.hitbox.inflate(self.interaction_margin * 2, self.interaction_margin * 2)

    def is_player_in_range(self, player_hitbox: pygame.Rect) -> bool:
        """Checks if player is in range for interaction."""
        return self.interaction_rect.colliderect(player_hitbox)

    def update(self, dt: float, *args, **kwargs):
        """NPC specific update logic."""
        pass