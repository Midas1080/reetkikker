# Example file showing a circle moving on screen
import pygame
from reetkikker.entities import ReetKikker

controls = {
    "up": pygame.K_w,
    "right": pygame.K_d,
    "down": pygame.K_s,
    "left": pygame.K_a,
    "lick": pygame.K_SPACE

}

controls2 = {
    "up": pygame.K_UP,
    "right": pygame.K_RIGHT,
    "down": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "lick": pygame.K_p

}

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 10

player_pos1 = pygame.Vector2(screen.get_width() / 4, screen.get_height() / 4)
player_pos2 = pygame.Vector2(screen.get_width() / 8, screen.get_height() / 8)

p1 = ReetKikker("green", 40, player_pos1, controls, 300)
p2 = ReetKikker("green", 40, player_pos2, controls2, 300)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("black")
    p1.render(screen)
    p1.update(dt)

    p2.render(screen)
    p2.update(dt)

    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
