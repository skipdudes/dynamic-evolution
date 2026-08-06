import pygame
from game.core.state import BaseState
from game.core.settings import FONT_UI, FONT_DIALOGUE, KEY_INTERACT, COLOR_TEXT_SELECTED, STRING_CONTINUE_PROMPT, \
    COLOR_TEXT_HELPER, COLOR_TEXT_MAIN
from game.states.transition_state import TransitionState


class StoryBoardState(BaseState):
    def __init__(self, state_machine, title: str, text: str, next_state, title_color=COLOR_TEXT_SELECTED,
                 hold_time=8.0):
        super().__init__(state_machine)
        self.next_state = next_state
        self.text_raw = text
        self.hold_time = hold_time  # Hold time before showing prompt

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
            if self.timer >= self.hold_time:
                self.can_skip = True

    def _proceed(self):
        self.is_transitioning = True
        transition = TransitionState(self.state_machine, self, self.next_state, duration=1.0)
        self.state_machine.change(transition)

    def _wrap_text_to_lines(self, text: str, font: pygame.font.Font, max_width: int) -> list[str]:
        """Wraps text properly, respecting both max width and explicit newlines (\n)."""
        lines = []
        paragraphs = text.split('\n')

        for paragraph in paragraphs:
            if not paragraph:  # Preserve empty lines for paragraph spacing
                lines.append("")
                continue

            words = paragraph.split(' ')
            current_line = []

            for word in words:
                test_line = ' '.join(current_line + [word])
                if font.size(test_line)[0] <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))

        return lines

    def draw(self, screen: pygame.Surface):
        screen.fill((0, 0, 0))

        screen_w = screen.get_width()
        screen_h = screen.get_height()

        # 1. Draw Title much higher to save vertical space
        screen.blit(self.title_surf, ((screen_w - self.title_surf.get_width()) // 2, 40))

        # 2. Handle Newlines and Wrapping dynamically
        max_text_width = screen_w - 160  # Wider text area (80px margin on each side)
        lines = self._wrap_text_to_lines(self.text_raw, self.font_text, max_text_width)

        # Reduce spacing between lines slightly to fit more text
        line_height = self.font_text.get_height() + 4

        # Start text much higher, right under the title
        start_y = 120

        for i, line in enumerate(lines):
            if line:  # Draw only if the line is not empty
                line_surf = self.font_text.render(line, True, COLOR_TEXT_MAIN)
                x = (screen_w - line_surf.get_width()) // 2
                y = start_y + (i * line_height)
                screen.blit(line_surf, (x, y))

        # 3. Draw static prompt at the very bottom edge to prevent overlapping
        if self.can_skip and not self.is_transitioning:
            prompt_y = screen_h - self.prompt_surf.get_height() - 20
            screen.blit(self.prompt_surf, ((screen_w - self.prompt_surf.get_width()) // 2, prompt_y))
