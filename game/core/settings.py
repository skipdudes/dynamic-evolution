import os
import pygame

# Window settings
WINDOW_WIDTH = 816
WINDOW_HEIGHT = 624
WINDOW_TITLE = "Shadows of the Crown II"
GAME_VERSION = "0.0.1"

# Game loop settings
MAX_UPDATETIME = 10  # ms (100 Hz logic update)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

LEVELS_DIR = os.path.join(ASSETS_DIR, "levels")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
ICON_PATH = os.path.join(IMAGES_DIR, "ui", "icon.png")

# Input Mappings (lists of allowed keys for each action)
KEY_UP = [pygame.K_w, pygame.K_UP]
KEY_DOWN = [pygame.K_s, pygame.K_DOWN]
KEY_LEFT = [pygame.K_a, pygame.K_LEFT]
KEY_RIGHT = [pygame.K_d, pygame.K_RIGHT]

KEY_INTERACT = [pygame.K_RETURN, pygame.K_z]
KEY_BACK = [pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_x]
KEY_MENU = [pygame.K_LCTRL, pygame.K_RCTRL, pygame.K_c]
KEY_PAUSE = [pygame.K_ESCAPE]
KEY_TOGGLE_FULLSCREEN = [pygame.K_F4]
KEY_DEBUG = [pygame.K_F3]
