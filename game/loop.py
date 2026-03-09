import pygame
import logging

log = logging.getLogger(__name__)

class Game:
    def __init__(self):
        pygame.init()
        # self.screen = pygame.display.set_mode((640, 480))
        self.screen = pygame.display.set_mode((1280, 960))
        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = 60
        self.dt = 0

        self.player_pos = pygame.Vector2(self.screen.get_width() / 2, self.screen.get_height() / 2)


    def run(self):
        log.info("Game started")

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # screen_rect = self.screen.get_rect()
            self.screen.fill("purple")
            pygame.draw.circle(self.screen, "red", self.player_pos, 40)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.player_pos.y -= 300 * self.dt
            if keys[pygame.K_s]:
                self.player_pos.y += 300 * self.dt
            if keys[pygame.K_a]:
                self.player_pos.x -= 300 * self.dt
            if keys[pygame.K_d]:
                self.player_pos.x += 300 * self.dt

            pygame.display.flip()
            self.dt = self.clock.tick(self.fps) / 1000


    def __del__(self):
        pygame.quit()
