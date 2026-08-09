import os
import pygame

# Window settings
WINDOW_WIDTH = 816
WINDOW_HEIGHT = 624
WINDOW_TITLE = "Shadows of the Crown II"
GAME_VERSION = "0.0.1"

# Game loop settings
MAX_UPDATETIME = 10  # ms (100 Hz logic update)

# LLM's specific name provided by the Groq API
LLM_NAME = "openai/gpt-oss-120b"

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
LEVELS_DIR = os.path.join(ASSETS_DIR, "levels")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
ICON_PATH = os.path.join(IMAGES_DIR, "ui", "icon.png")

# Menu assets
IMAGE_LOGO = os.path.join(IMAGES_DIR, "ui", "logo.png")
IMAGE_MAIN_MENU_BG = os.path.join(IMAGES_DIR, "titles", "Night.png")
IMAGE_OPTIONS_BG = os.path.join(IMAGES_DIR, "titles", "WorldMap.png")
IMAGE_ABOUT_BG = os.path.join(IMAGES_DIR, "titles", "Book.png")

# Start Level (after Prologue)
LEVEL_START = "castle.tmx"

# Input Mappings (lists of allowed keys for each action)
KEY_UP = [pygame.K_w, pygame.K_UP]
KEY_DOWN = [pygame.K_s, pygame.K_DOWN]
KEY_LEFT = [pygame.K_a, pygame.K_LEFT]
KEY_RIGHT = [pygame.K_d, pygame.K_RIGHT]
KEY_INTERACT = [pygame.K_RETURN, pygame.K_z]
KEY_RETURN = [pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_x, pygame.K_ESCAPE]
KEY_INVENTORY = [pygame.K_i, pygame.K_e, pygame.K_TAB]
KEY_JOURNAL = [pygame.K_n, pygame.K_l]
KEY_PAUSE = [pygame.K_ESCAPE]
KEY_FULLSCREEN = [pygame.K_F4]
KEY_DEBUG = [pygame.K_F3]
KEY_NIGHTMODE = [pygame.K_F5]

# Fonts (Tuple: Path, Size)
FONT_SPLASH = (os.path.join(FONTS_DIR, "CelticTime.ttf"), 48)
FONT_UI = (os.path.join(FONTS_DIR, "CelticTime.ttf"), 32)
FONT_DIALOGUE = (os.path.join(FONTS_DIR, "CelticTime.ttf"), 32)

# Configuration
CONFIG_FILE_PATH = os.path.join(BASE_DIR, "options.ini")
DEFAULT_FPS = 60
DEFAULT_FULLSCREEN = False
FPS_CHOICES = [30, 60, 120, 0]

# HUD Settings
HUD_NOTIFICATION_DURATION = 5.0
STRING_NOTIFY_ITEM = "New item: "
STRING_NOTIFY_QUEST = "New log entry: "

# Splash text
STRING_SPLASH_TEXT = "skipdudes presents..."

# Menu strings
MENU_OPTION_START = "Start Game"
MENU_OPTION_OPTIONS = "Options"
MENU_OPTION_ABOUT = "About"
MENU_OPTION_END = "Quit Game"

# Options Menu Strings
STRING_OPTIONS_TITLE = "Options"
STRING_OPTIONS_FPS = "FPS Limit"
STRING_OPTIONS_DISPLAY = "Display Mode"
STRING_OPTIONS_WINDOWED = "Windowed"
STRING_OPTIONS_FULLSCREEN = "Fullscreen"
STRING_OPTIONS_UNLIMITED = "Unlimited"

STRING_CONTROLS_TITLE = "--- Controls ---"
STRING_CONTROLS_MOVE = "Movement: Arrows / WSAD"
STRING_CONTROLS_INTERACT = "Interact: ENTER / Z"
STRING_CONTROLS_RETURN = "Back: SHIFT / X"
STRING_CONTROLS_INVENTORY = "Inventory: TAB / I / E"
STRING_CONTROLS_JOURNAL = "Journal: N / L"
STRING_CONTROLS_PAUSE = "Pause: ESC"
STRING_CONTROLS_FULLSCREEN = "Fullscreen: F4"

STRING_OPTIONS_BACK = "Return"

# About Menu Strings
STRING_ABOUT_TITLE = "About"
STRING_ABOUT_TEXT = (
    "Shadows of the Crown II\n"
    "Master's Thesis Project - 2026\n\n"
    "Created by: Marcin Chetnik (aka skipdudes)\n"
    "github.com/skipdudes/dynamic-evolution"
)
STRING_ABOUT_BACK = "Press ENTER to return"

# Pause Menu Strings
STRING_PAUSE_TITLE = "Paused"
STRING_PAUSE_RESUME = "Resume"
STRING_PAUSE_OPTIONS = "Options"
STRING_PAUSE_MAIN_MENU = "Main Menu"
STRING_PAUSE_QUIT = "Quit Game"
STRING_PAUSE_WARNING = "All story progress will be lost!"

# Prologue
STRING_PROLOGUE_HEADER = "A False Peace"
STRING_PROLOGUE_TEXT = """You remained loyal to the crown. The rebellion in the capital was crushed, its leaders executed, and King Arthur retained his throne. For your bravery, you were named Duke.

The citizens believed peace had finally returned. But it was merely an illusion.

While clearing out the rebels' hideouts, a disturbing detail emerged. Many of the traitors carried the exact same item: a small, ferret-shaped amulet. The conspiracy was much deeper than anyone anticipated.

You have been urgently summoned to the castle. The true Shadows of the Crown are still out there..."""

# Starting quest first entry
STRING_FIRST_LOG_ENTRY = "The King summoned me urgently. I should speak with him in the throne room."

# Quest entry upon breaking letter's seal
STRING_BREAK_SEAL_LOG_ENTRY = "I broke the seal and opened the letter. It mentions a closed estate next to the hideout and is signed 'H'. Who from the capital is behind this?"

# In-game strings
STRING_RETURN_PROMPT = "Press ESC to return"
STRING_CONTINUE_PROMPT = "Press ENTER to continue"
STRING_DIALOGUE_BEGIN_PROMPT = "Press ENTER to speak with "
STRING_DIALOGUE_EMPTY = "Enter text. Press ESC to quit"
STRING_DIALOGUE_CONFIRM = "Press ENTER to confirm, press ESC to quit"
STRING_DIALOGUE_WAIT = "Wait for the response"
STRING_DIALOGUE_REPLY = "Press ENTER to reply, press ESC to quit"
STRING_DIALOGUE_NO_REPLY_NPC = "*nods silently*"
STRING_DIALOGUE_TOO_MANY = "Too many characters!"
STRING_DIALOGUE_SCROLL_UP = "[^ Scroll Up]"
STRING_DIALOGUE_SCROLL_DOWN = "[v Scroll Down]"
STRING_INVENTORY_TITLE = "Inventory"
STRING_INVENTORY_EMPTY = "Your inventory is empty."
STRING_JOURNAL_TITLE = "Quest Journal"
STRING_JOURNAL_EMPTY = "You have no quests."
STRING_JOURNAL_ACTIVE = "[ Active ]"
STRING_JOURNAL_COMPLETED = "[ Completed ]"
STRING_JOURNAL_READ_PROMPT = "Press ENTER to read entries"
STRING_BREAK_SEAL_PROMPT = "Press ENTER to break the seal"

# UI Colors
COLOR_UI_BG_ALPHA = (0, 0, 0, 153)          # 60% opacity black
COLOR_UI_BOX_ALPHA = (0, 0, 0, 230)         # 90% opacity black
COLOR_TEXT_MAIN = (255, 255, 255)           # White
COLOR_TEXT_SELECTED = (255, 215, 0)         # Gold
COLOR_TEXT_HELPER = (128, 128, 128)         # Gray
COLOR_TEXT_WARNING = (255, 0, 0)            # Red
COLOR_PREFIX_PLAYER = (255, 215, 0)         # Gold
COLOR_PREFIX_NPC = (255, 215, 0)            # Gold
COLOR_PREFIX_THINKING = (255, 255, 255)     # White
COLOR_MISSING = (255, 0, 255)               # Color used for missing textures (magenta)
COLOR_NIGHT_FILTER = (15, 15, 45, 160)      # Dark blueish-purple for a cinematic night feel
