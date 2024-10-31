from typing import Tuple
import pygame


# TODO generate KEY bindings to make it easy to create multiple individual users

class Player:
    def __init__(self, screen, init_position: Tuple[int, int], movement_speed=300):
        self.screen = screen
        self.position = init_position
        self.movement_speed = movement_speed
        self._draw()
        self.projectile = None

    def _draw(self):
        pygame.draw.circle(self.screen, "red", self.position, 40)

    def update(self, dt, keys):
        if not self.projectile:
            if keys[pygame.K_w]:
                self.position.y -= self.movement_speed * dt
            if keys[pygame.K_s]:
                self.position.y += self.movement_speed * dt
            if keys[pygame.K_a]:
                self.position.x -= self.movement_speed * dt
            if keys[pygame.K_d]:
                self.position.x += self.movement_speed * dt
            if keys[pygame.K_SPACE]:
                self.projectile = Projectile(self.screen, self.position, 500)
                self._draw()
        else:
            self.projectile.update(dt, keys)


class Projectile(Player):
    def __init__(self, screen, init_position: Tuple[int, int], movement_speed=300, parent=None):
        self.screen = screen
        self.position = init_position
        self.movement_speed = movement_speed
        self._draw()
        self.projectile = None
        self.parent = parent

    def _draw(self):
        pygame.draw.circle(self.screen, "blue", self.position, 10)

    def update(self, dt, keys):
        self.spa
