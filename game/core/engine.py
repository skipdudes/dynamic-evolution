import pygame
import logging
import os
from game.core.state_machine import StateMachine
from game.core.settings import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, MAX_UPDATETIME, GAME_VERSION, ICON_PATH, KEY_FULLSCREEN

log = logging.getLogger(__name__)

class Engine:
    def __init__(self, width: int = WINDOW_WIDTH, height: int = WINDOW_HEIGHT):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height), pygame.SCALED)
        pygame.display.set_caption(f"{WINDOW_TITLE} v{GAME_VERSION}")
        pygame.mouse.set_visible(False)

        if os.path.exists(ICON_PATH):
            icon_surface = pygame.image.load(ICON_PATH).convert_alpha()
            pygame.display.set_icon(icon_surface)

        self.running = True
        self.target_fps = 60
        self.state_machine = StateMachine()

    def run(self):
        log.info("Starting the game loop")

        last_frame_start_time = pygame.time.get_ticks()
        time_accumulator = 0

        while self.running:
            # Calculate the time between the frames
            current_frame_start_time = pygame.time.get_ticks()
            elapsed_frame_time = current_frame_start_time - last_frame_start_time
            last_frame_start_time = current_frame_start_time

            # PREVENT SPIRAL OF DEATH (Catch-up cap)
            if elapsed_frame_time > 10 * MAX_UPDATETIME:
                elapsed_frame_time = 10 * MAX_UPDATETIME  # up to 10 frames back

            time_accumulator += elapsed_frame_time

            # Handle discrete events and global engine inputs
            self.handle_events()

            # Handle continuous inputs
            keys = pygame.key.get_pressed()
            self.state_machine.handle_input(keys)

            # Update with fixed time step
            while time_accumulator >= MAX_UPDATETIME:
                self.state_machine.update(MAX_UPDATETIME / 1000.0)
                time_accumulator -= MAX_UPDATETIME

            # Render
            self.render()

            # Cap the framerate dynamically
            if self.target_fps > 0:
                min_frametime = 1000 // self.target_fps
                frame_time = pygame.time.get_ticks() - current_frame_start_time
                if frame_time < min_frametime:
                    pygame.time.delay(min_frametime - frame_time)

        log.info("Finished the game loop")
        self.quit()

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in KEY_FULLSCREEN:
                    pygame.display.toggle_fullscreen()
                    log.info("Toggled fullscreen mode.")

        # Pass the events down to current states
        self.state_machine.handle_events(events)

    def render(self):
        # Pygame handles the buffer swap via display.flip(), scaling is handled by SCALED flag
        self.state_machine.draw(self.screen)
        pygame.display.flip()

    def set_fps_limit(self, new_fps: int):
        """
        Dynamically changes the FPS limit.
        Pass 0 for unlimited framerate.
        """
        log.info(f"Changing FPS limit to: {'Unlimited' if new_fps == 0 else new_fps}")
        self.target_fps = new_fps

    def quit(self):
        pygame.quit()
