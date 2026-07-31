import os
import pygame
import logging
from game.core.state import BaseState
from game.core.settings import (
    FONT_UI, FONT_DIALOGUE, IMAGE_OPTIONS_BG, KEY_RETURN, KEY_INTERACT,
    KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, GAME_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT,
    COLOR_TEXT_MAIN, COLOR_TEXT_SELECTED, COLOR_TEXT_HELPER, FPS_CHOICES, DEFAULT_FPS,
    STRING_OPTIONS_TITLE, STRING_OPTIONS_FPS, STRING_OPTIONS_DISPLAY,
    STRING_OPTIONS_WINDOWED, STRING_OPTIONS_FULLSCREEN, STRING_OPTIONS_UNLIMITED,
    STRING_CONTROLS_TITLE, STRING_CONTROLS_MOVE, STRING_CONTROLS_INTERACT,
    STRING_CONTROLS_PAUSE, STRING_CONTROLS_FULLSCREEN, STRING_OPTIONS_BACK,
    # Nowe importy:
    STRING_CONTROLS_RETURN, STRING_CONTROLS_INVENTORY, STRING_CONTROLS_JOURNAL
)

log = logging.getLogger(__name__)

class OptionsState(BaseState):
    def __init__(self, state_machine):
        super().__init__(state_machine)

        self.font_title = pygame.font.Font(FONT_UI[0], 48)
        self.font_menu = pygame.font.Font(*FONT_UI)
        self.font_info = pygame.font.Font(*FONT_DIALOGUE)

        self.bg_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        if os.path.exists(IMAGE_OPTIONS_BG):
            self.bg_surface = pygame.image.load(IMAGE_OPTIONS_BG).convert()
        else:
            self.bg_surface.fill((30, 30, 50))

        # Added the return option as the third interactive element
        self.options = [STRING_OPTIONS_FPS, STRING_OPTIONS_DISPLAY, STRING_OPTIONS_BACK]
        self.selected_index = 0

        # Zaktualizowana lista sterowania z nowymi stringami
        self.controls_info = [
            STRING_CONTROLS_TITLE,
            STRING_CONTROLS_MOVE,
            STRING_CONTROLS_INTERACT,
            STRING_CONTROLS_RETURN,
            STRING_CONTROLS_INVENTORY,
            STRING_CONTROLS_JOURNAL,
            STRING_CONTROLS_PAUSE,
            STRING_CONTROLS_FULLSCREEN
        ]

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_RETURN:
                    self.state_machine.pop()
                elif event.key in KEY_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key in KEY_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key in KEY_LEFT:
                    self._toggle_value(direction=-1)
                elif event.key in KEY_RIGHT:
                    self._toggle_value(direction=1)
                elif event.key in KEY_INTERACT:
                    if self.selected_index == 2:  # if on the "Return" option
                        self.state_machine.pop()  # go back
                    else:
                        self._toggle_value(direction=1)

    def _toggle_value(self, direction: int):
        if self.selected_index == 0:  # FPS Limit
            current_fps = getattr(self.state_machine.engine, 'target_fps', DEFAULT_FPS)
            idx = FPS_CHOICES.index(current_fps) if current_fps in FPS_CHOICES else 1
            new_fps = FPS_CHOICES[(idx + direction) % len(FPS_CHOICES)]
            self.state_machine.engine.set_fps_limit(new_fps)

        elif self.selected_index == 1:  # Display Mode
            pygame.display.toggle_fullscreen()
            is_full = bool(pygame.display.get_surface().get_flags() & pygame.FULLSCREEN)
            self.state_machine.engine.config.fullscreen = is_full
            self.state_machine.engine.config.save()
            log.info("Display mode toggled from menu.")

    def draw(self, screen: pygame.Surface):
        screen.blit(self.bg_surface, (0, 0))

        # Zwiększyłem wysokość panelu z 450 na 520, żeby pomieścić 3 dodatkowe linijki tekstu
        panel_width, panel_height = 500, 520
        ui_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(ui_surface, (0, 0, 0, 200), ui_surface.get_rect(), border_radius=12)

        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        screen.blit(ui_surface, (panel_x, panel_y))

        title_surf = self.font_title.render(STRING_OPTIONS_TITLE, True, COLOR_TEXT_SELECTED)
        screen.blit(title_surf, ((WINDOW_WIDTH - title_surf.get_width()) // 2, panel_y + 30))

        current_fps = getattr(self.state_machine.engine, 'target_fps', DEFAULT_FPS)
        is_fullscreen = bool(pygame.display.get_surface().get_flags() & pygame.FULLSCREEN)

        start_y = panel_y + 100  # Podniesione ciut wyżej

        for i, option in enumerate(self.options):
            color = COLOR_TEXT_SELECTED if i == self.selected_index else COLOR_TEXT_MAIN

            if i < 2:  # Value-based options (FPS and Display)
                val_string = ""
                if i == 0:
                    val_string = STRING_OPTIONS_UNLIMITED if current_fps == 0 else str(current_fps)
                elif i == 1:
                    val_string = STRING_OPTIONS_FULLSCREEN if is_fullscreen else STRING_OPTIONS_WINDOWED

                text = f"{option}:  < {val_string} >"
                text_surf = self.font_menu.render(text, True, color)

                x = (WINDOW_WIDTH - text_surf.get_width()) // 2
                y = start_y + (i * 40)  # Opcje są teraz ciaśniej upakowane (co 40px)
                screen.blit(text_surf, (x, y))
            else:
                text_surf = self.font_menu.render(option, True, color)
                x = (WINDOW_WIDTH - text_surf.get_width()) // 2
                y = panel_y + panel_height - 50  # Przycisk powrotu bezpiecznie na dole
                screen.blit(text_surf, (x, y))

        # Blok z informacjami o sterowaniu (zaczyna się 90px pod pierwszą opcją)
        info_start_y = start_y + 90
        for i, line in enumerate(self.controls_info):
            info_surf = self.font_info.render(line, True, COLOR_TEXT_HELPER)
            x = (WINDOW_WIDTH - info_surf.get_width()) // 2
            y = info_start_y + (i * 30)
            screen.blit(info_surf, (x, y))

        version_surf = self.font_info.render(f"v{GAME_VERSION}", True, COLOR_TEXT_MAIN)
        screen.blit(version_surf,
                    (WINDOW_WIDTH - version_surf.get_width() - 20, WINDOW_HEIGHT - version_surf.get_height() - 15))
