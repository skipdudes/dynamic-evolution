import os
import configparser
import logging
from game.core.settings import CONFIG_FILE_PATH, DEFAULT_FPS, DEFAULT_FULLSCREEN, FPS_CHOICES

log = logging.getLogger(__name__)

class ConfigManager:
    """Handles saving and loading user preferences from an .ini file."""

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.fps = DEFAULT_FPS
        self.fullscreen = DEFAULT_FULLSCREEN
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE_PATH):
            self.config.read(CONFIG_FILE_PATH)
            try:
                loaded_fps = self.config.getint('Video', 'fps', fallback=DEFAULT_FPS)
                self.fps = loaded_fps if loaded_fps in FPS_CHOICES else DEFAULT_FPS

                self.fullscreen = self.config.getboolean('Video', 'fullscreen', fallback=DEFAULT_FULLSCREEN)
                log.info("Loaded configuration from options.ini")
            except Exception as e:
                log.warning(f"Failed to parse config, using defaults. Error: {e}")
                self.fps = DEFAULT_FPS
                self.fullscreen = DEFAULT_FULLSCREEN
        else:
            self.save()  # Create the file with default values

    def save(self):
        if not self.config.has_section('Video'):
            self.config.add_section('Video')

        self.config.set('Video', 'fps', str(self.fps))
        self.config.set('Video', 'fullscreen', str(self.fullscreen))

        with open(CONFIG_FILE_PATH, 'w') as f:
            self.config.write(f)
        log.info(f"Saved configuration to {CONFIG_FILE_PATH}")
