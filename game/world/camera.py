import pygame
from game.core.settings import WINDOW_WIDTH, WINDOW_HEIGHT

class Camera:
    def __init__(self, map_width: int, map_height: int):
        self.map_width = map_width
        self.map_height = map_height

        # camera_x and camera_y represent the top-left corner of the view
        self.x = 0.0
        self.y = 0.0

    def update(self, target_x: float, target_y: float, target_width: int, target_height: int):
        """
        Centers the camera on the target (e.g. player) and clamps it to map boundaries.
        Locks coordinates to integers to prevent sub-pixel rendering jitter.
        """
        # Calculate ideal center position
        ideal_x = target_x + (target_width / 2) - (WINDOW_WIDTH / 2)
        ideal_y = target_y + (target_height / 2) - (WINDOW_HEIGHT / 2)

        # Clamp to map boundaries so we don't show black areas outside the map
        clamped_x = max(0.0, min(ideal_x, self.map_width - WINDOW_WIDTH))
        clamped_y = max(0.0, min(ideal_y, self.map_height - WINDOW_HEIGHT))

        # Convert to integer to eliminate sub-pixel camera jitter
        self.x = int(clamped_x)
        self.y = int(clamped_y)

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        """
        Shifts a rectangle by the camera's offset. Useful for debug drawing.
        """
        return pygame.Rect(rect.x - self.x, rect.y - self.y, rect.width, rect.height)
