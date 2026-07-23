import pygame
from game.entities.entity import Entity

class NPC(Entity):
    def __init__(self, x: float, y: float, npc_id: str, width: int = 48, height: int = 72):
        # Pass dimensions down to the base Entity class
        super().__init__(x, y, width=width, height=height)
        self.npc_id: str = npc_id

        # Interaction radius (added to the feet hitbox)
        self.interaction_margin: int = 16

        # NPC visual placeholder
        self.current_sprite = pygame.Surface((self.width, self.height))
        self.current_sprite.fill((255, 215, 0))  # Gold color

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