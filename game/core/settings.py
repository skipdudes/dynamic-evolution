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
# KEY_BACK = [pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_x]
# KEY_MENU = [pygame.K_LCTRL, pygame.K_RCTRL, pygame.K_c]
KEY_PAUSE = [pygame.K_ESCAPE]
KEY_FULLSCREEN = [pygame.K_F4]
KEY_DEBUG = [pygame.K_F3]

# Fonts (Tuple: Path, Size)
FONT_UI = (os.path.join(FONTS_DIR, "CelticTime.ttf"), 32)
FONT_DIALOGUE = (os.path.join(FONTS_DIR, "CelticTime.ttf"), 32)

# In-game strings
STRING_DIALOGUE_BEGIN_PROMPT = "Press ENTER to speak with "

STRING_DIALOGUE_EMPTY = "Enter text. Press ESC to quit"
STRING_DIALOGUE_CONFIRM = "Press ENTER to confirm, press ESC to quit"
STRING_DIALOGUE_WAIT = "Wait for the response"
STRING_DIALOGUE_REPLY = "Press ENTER to reply, press ESC to quit"
STRING_DIALOGUE_TOO_MANY = "Too many characters!"
STRING_DIALOGUE_SCROLL_UP = "[^ Scroll Up]"
STRING_DIALOGUE_SCROLL_DOWN = "[v Scroll Down]"

COLOR_MISSING = (255, 0, 255)  # Color used for missing textures (magenta)
