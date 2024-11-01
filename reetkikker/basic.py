# Example file showing a circle moving on screen
import pygame
from reetkikker.entities import ReetKikker, default_renderer

controls = {
    "up": pygame.K_w,
    "right": pygame.K_d,
    "down": pygame.K_s,
    "left": pygame.K_a

}

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 10

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
player_pos1 = pygame.Vector2(screen.get_width() / 4, screen.get_height() / 4)
p1 = ReetKikker("green", 40, player_pos1, controls, 300)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("black")
    keys = pygame.key.get_pressed()
    default_renderer(p1, screen)
    p1.update(dt)

    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
