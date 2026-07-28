import pygame
from game.core.state import BaseState
from game.core.settings import (
    FONT_UI, FONT_DIALOGUE, KEY_PAUSE, KEY_UP, KEY_DOWN, KEY_INTERACT,
    WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_TEXT_SELECTED, COLOR_TEXT_MAIN, COLOR_TEXT_WARNING,
    STRING_PAUSE_TITLE, STRING_PAUSE_RESUME, STRING_PAUSE_OPTIONS,
    STRING_PAUSE_MAIN_MENU, STRING_PAUSE_QUIT, STRING_PAUSE_WARNING
)
from game.states.options_state import OptionsState
from game.states.transition_state import TransitionState

class PauseState(BaseState):
    def __init__(self, state_machine, play_state):
        super().__init__(state_machine)
        self.play_state = play_state

        self.font_title = pygame.font.Font(FONT_UI[0], 48)
        self.font_menu = pygame.font.Font(*FONT_UI)
        self.font_info = pygame.font.Font(*FONT_DIALOGUE)

        self.options = [
            STRING_PAUSE_RESUME,
            STRING_PAUSE_OPTIONS,
            STRING_PAUSE_MAIN_MENU,
            STRING_PAUSE_QUIT
        ]
        self.selected_index = 0

        self.overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 150))

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_PAUSE:
                    self.state_machine.pop()
                elif event.key in KEY_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key in KEY_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key in KEY_INTERACT:
                    self._handle_selection()

    def _handle_selection(self):
        selected = self.options[self.selected_index]

        if selected == STRING_PAUSE_RESUME:
            self.state_machine.pop()

        elif selected == STRING_PAUSE_OPTIONS:
            # Pushes options as an overlay; returning will pop it and reveal pause menu again
            self.state_machine.push(OptionsState(self.state_machine))

        elif selected == STRING_PAUSE_MAIN_MENU:
            from game.states.main_menu_state import MainMenuState

            def load_main_menu():
                return MainMenuState(self.state_machine)

            transition = TransitionState(self.state_machine, self, next_state_func=load_main_menu, duration=0.5)
            self.state_machine.change(transition)

        elif selected == STRING_PAUSE_QUIT:
            transition = TransitionState(self.state_machine, self, None, duration=0.5, is_quit=True)
            self.state_machine.change(transition)

    def draw(self, screen: pygame.Surface):
        self.play_state.draw(screen)
        screen.blit(self.overlay, (0, 0))

        panel_width, panel_height = 400, 360
        ui_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(ui_surface, (0, 0, 0, 200), ui_surface.get_rect(), border_radius=12)

        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        screen.blit(ui_surface, (panel_x, panel_y))

        title_surf = self.font_title.render(STRING_PAUSE_TITLE, True, COLOR_TEXT_SELECTED)
        screen.blit(title_surf, ((WINDOW_WIDTH - title_surf.get_width()) // 2, panel_y + 30))

        start_y = panel_y + 110
        for i, option in enumerate(self.options):
            color = COLOR_TEXT_SELECTED if i == self.selected_index else COLOR_TEXT_MAIN
            text_surf = self.font_menu.render(option, True, color)

            x = (WINDOW_WIDTH - text_surf.get_width()) // 2
            y = start_y + (i * 45)
            screen.blit(text_surf, (x, y))

        # Warning logic for both "Main Menu" and "Quit Game" selections
        if self.options[self.selected_index] in (STRING_PAUSE_MAIN_MENU, STRING_PAUSE_QUIT):
            warning_surf = self.font_info.render(STRING_PAUSE_WARNING, True, COLOR_TEXT_WARNING)
            x = (WINDOW_WIDTH - warning_surf.get_width()) // 2
            y = panel_y + panel_height - 40
            screen.blit(warning_surf, (x, y))
