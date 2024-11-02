from typing import Callable, Protocol, TypedDict, Optional, Iterable
from pygame import Surface, Vector2
from itertools import chain
import pygame

renderer = Callable[['Renderable', Surface], None]


class TongueInactiveException(Exception):
    pass


class RenderInformation(TypedDict):
    color: str
    radius: int
    position: Vector2


class KeyBindings(TypedDict):
    up: int
    right: int
    down: int
    left: int
    lick: int


class Renderable(Protocol):
    def get_render_information(self) -> Iterable[RenderInformation]:
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

    def get_render_information(self) -> Iterable[RenderInformation]:
        x = [{"color": self.color, "radius": self.radius, "position": self.position}]
        return x


def default_renderer(e: Renderable, screen: Surface):
    to_render = e.get_render_information()
    for ri in to_render:
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
        if keys[self.key_binding['lick']]:
            self.tongue = Tongue("red", 10, self.position.copy(), self.key_binding, self.movement_speed * 1.5)

    def get_render_information(self) -> Iterable[RenderInformation]:
        own = super().get_render_information()
        x = chain(own, self.tongue.get_render_information()) if self.tongue else own
        return x

    def update_tongue(self, dt):
        try:
            self.tongue.update(dt)
        except TongueInactiveException:
            self.tongue = None

    def update(self, dt):
        if self.tongue:
            self.update_tongue(dt)
        else:
            self.update_self(dt)


class Tongue(Entity):
    def __init__(self, color: str, radius: int, position: Vector2, key_bindings: KeyBindings,
                 movement_speed: int):
        super().__init__(color, radius, position, key_bindings, movement_speed)
        self.tongue: Optional[Entity] = None
        self.retracting = False

    def get_render_information(self) -> Iterable[RenderInformation]:
        own = super().get_render_information()
        return chain(own, self.tongue.get_render_information()) if self.tongue else own

    def update_self(self, dt: int) -> None:
        keys = pygame.key.get_pressed()
        if not keys[self.key_binding['lick']] or self.retracting:  # destruct tongue
            raise TongueInactiveException()
        nw_position = self.position.copy()
        if keys[self.key_binding['up']]:
            nw_position.y += self.movement_speed * dt
        if keys[self.key_binding['right']]:
            nw_position.x += self.movement_speed * dt
        if keys[self.key_binding['down']]:
            nw_position.y -= self.movement_speed * dt
        if keys[self.key_binding['left']]:
            nw_position.x -= self.movement_speed * dt
        # spawn new tip of tongue
        self.tongue = Tongue(self.color, self.radius, nw_position, self.key_binding, self.movement_speed)

    def update(self, dt: int) -> None:
        if self.tongue:  # hand over control to tip of tongue
            try:
                self.tongue.update(dt)
            except TongueInactiveException:
                self.tongue = None
                self.retracting = True
        else:
            self.update_self(dt)
