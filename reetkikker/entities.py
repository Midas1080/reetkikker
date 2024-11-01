from typing import Callable, Protocol, TypedDict, Optional
from pygame import Surface, Vector2
import pygame

renderer = Callable[['Renderable', Surface], None]


class RenderInformation(TypedDict):
    color: str
    radius: int
    position: Vector2


class KeyBindings(TypedDict):
    up: int
    right: int
    down: int
    left: int


class Renderable(Protocol):
    def get_render_information(self) -> RenderInformation:
        pass


class Updatable(Protocol):
    def update(self, dt: int) -> None:
        pass


class Entity(Updatable, Renderable):
    def __init__(self, color: str, radius: int, position: Vector2, key_bindings: KeyBindings,
                 movement_speed: int):
        self.color = color
        self.radius = radius
        self.position = position
        self.key_binding = key_bindings
        self.movement_speed = movement_speed

    def update(self, dt: int) -> None:
        pass

    def get_render_information(self) -> RenderInformation:
        x = {"color": self.color, "radius": self.radius, "position": self.position}
        return x


def default_renderer(e: Renderable, screen: Surface):
    ri = e.get_render_information()
    pygame.draw.circle(screen, ri['color'], ri['position'], ri['radius'])


class ReetKikker(Entity):
    def __init__(self, color: str, radius: int, position: Vector2, key_bindings: KeyBindings,
                 movement_speed: int):
        super().__init__(color, radius, position, key_bindings, movement_speed)
        self.tongue: Optional[Entity] = None

    def update_self(self, dt):
        keys = pygame.key.get_pressed()
        if keys[self.key_binding['up']]:
            self.position.y += self.movement_speed * dt
        if keys[self.key_binding['right']]:
            self.position.x += self.movement_speed * dt
        if keys[self.key_binding['down']]:
            self.position.y -= self.movement_speed * dt
        if keys[self.key_binding['left']]:
            self.position.x -= self.movement_speed * dt

    def update(self, dt):
        if self.tongue:
            self.tongue.update(dt)
        else:
            self.update_self(dt)
