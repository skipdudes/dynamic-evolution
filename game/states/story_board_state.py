import pygame
from game.core.state import BaseState
from game.core.settings import FONT_UI, FONT_DIALOGUE, KEY_INTERACT, COLOR_TEXT_SELECTED, STRING_CONTINUE_PROMPT, COLOR_TEXT_HELPER, COLOR_TEXT_MAIN
from game.states.transition_state import TransitionState

class StoryBoardState(BaseState):
    def __init__(self, state_machine, title: str, text: str, next_state, title_color=COLOR_TEXT_SELECTED):
        super().__init__(state_machine)
        self.next_state = next_state
        self.text_raw = text

        self.font_title = pygame.font.Font(FONT_UI[0], 48)
        self.font_text = pygame.font.Font(*FONT_DIALOGUE)
        self.font_prompt = pygame.font.Font(*FONT_UI)

        self.title_surf = self.font_title.render(title, True, title_color)
        self.prompt_surf = self.font_prompt.render(STRING_CONTINUE_PROMPT, True, COLOR_TEXT_HELPER)

        self.timer = 0.0
        self.can_skip = False
        self.is_transitioning = False

    def handle_events(self, events: list[pygame.event.Event]):
        if self.is_transitioning:
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_INTERACT and self.can_skip:
                    self._proceed()

    def update(self, dt: float):
        if not self.can_skip and not self.is_transitioning:
            self.timer += dt
            if self.timer >= 3.0:  # Hold time before showing prompt
                self.can_skip = True

    def _proceed(self):
        self.is_transitioning = True
        transition = TransitionState(self.state_machine, self, self.next_state, duration=1.0)
        self.state_machine.change(transition)

    def draw(self, screen: pygame.Surface):
        screen.fill((0, 0, 0))

        # Draw Title
        screen.blit(self.title_surf, ((screen.get_width() - self.title_surf.get_width()) // 2, 100))

        # Handle Newlines in main text
        lines = self.text_raw.split('\n')
        line_height = self.font_text.get_height() + 10
        start_y = 220

        for i, line in enumerate(lines):
            line_surf = self.font_text.render(line.strip(), True, COLOR_TEXT_MAIN)
            x = (screen.get_width() - line_surf.get_width()) // 2
            y = start_y + (i * line_height)
            screen.blit(line_surf, (x, y))

        # Draw static prompt (no blinking) and hide it when transitioning
        if self.can_skip and not self.is_transitioning:
            screen.blit(self.prompt_surf, ((screen.get_width() - self.prompt_surf.get_width()) // 2, 500))
