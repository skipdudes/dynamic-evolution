import pygame

class Entity:
    """Base class for all characters and movable objects on the map."""

    def __init__(self, x: float, y: float, width: int = 48, height: int = 72, hitbox_width: int = 36, hitbox_height: int = 24):
        self.x: float = x
        self.y: float = y
        self.width: int = width
        self.height: int = height

        # Hitbox dimensions and offsets
        self.hitbox_width: int = hitbox_width
        self.hitbox_height: int = hitbox_height
        self.hitbox_offset_x: int = (self.width - self.hitbox_width) // 2
        self.hitbox_offset_y: int = self.height - self.hitbox_height

        # Internal default surface storage
        self._sprite: pygame.Surface = pygame.Surface((self.width, self.height))
        self._sprite.fill((200, 200, 200))

    @property
    def bottom(self) -> float:
        """Reference point for Y-Sorting (character's feet)."""
        return self.y + self.height

    @property
    def hitbox(self) -> pygame.Rect:
        """Dynamically calculates current hitbox rect based on position and offsets."""
        return pygame.Rect(
            int(self.x + self.hitbox_offset_x),
            int(self.y + self.hitbox_offset_y),
            self.hitbox_width,
            self.hitbox_height
        )

    @property
    def current_sprite(self) -> pygame.Surface:
        """Returns the current surface to draw."""
        return self._sprite

    @current_sprite.setter
    def current_sprite(self, value: pygame.Surface):
        """Allows setting a static sprite surface directly."""
        self._sprite = value

    def update(self, dt: float, *args, **kwargs):
        """Abstract method for derivative classes."""
        pass
