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

# UI Colors
COLOR_UI_BG_ALPHA = (0, 0, 0, 153)          # 60% opacity black
COLOR_UI_BOX_ALPHA = (0, 0, 0, 230)         # 90% opacity black
COLOR_TEXT_MAIN = (255, 255, 255)           # White
COLOR_TEXT_HELPER = (128, 128, 128)         # Gray
COLOR_TEXT_WARNING = (255, 0, 0)            # Red
COLOR_PREFIX_PLAYER = (255, 215, 0)         # Gold
COLOR_PREFIX_NPC = (255, 215, 0)            # Gold
COLOR_PREFIX_THINKING = (255, 255, 255)     # White
COLOR_MISSING = (255, 0, 255)               # Color used for missing textures (magenta)

# LLM Base Context (Shared across all characters)
LLM_SYSTEM_BASE_CONTEXT = (
    "You are an NPC in a 2D RPG game called 'Shadows of the Crown II'. "
    "Keep your answers concise and immersive. Do not break character. "
    "Do not acknowledge that you are an AI."
)
