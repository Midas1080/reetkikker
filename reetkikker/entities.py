from typing import Callable, Protocol, TypedDict, Optional, Iterable, Literal
from pygame import Surface, Vector2
from itertools import chain
import pygame
from pygame.sprite import Sprite

Direction = Optional[Literal["up", "right", "down", "left"]]
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


class Entity(Sprite, Updatable, Renderable):
    def __init__(self, color: str, radius: int, position: Vector2, key_bindings: KeyBindings,
                 movement_speed: int, direction=None):
        super().__init__()
        self.color = color
        self.radius = radius
        self.position = position
        self.key_binding = key_bindings
        self.movement_speed = movement_speed
        self.direction: Direction = direction

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.position, (self.radius // 4, self.radius // 4))

    def update(self, dt: int) -> None:
        pass

    def get_render_information(self) -> Iterable[RenderInformation]:
        x = [{"color": self.color, "radius": self.radius, "position": self.position}]
        return x


def default_renderer(e: Renderable, screen: Surface):
    to_render = e.get_render_information()
    for ri in to_render:
        h = 2 * ri['radius']
        # pygame.draw.circle(screen, ri['color'], ri['position'], ri['radius'])
        pygame.draw.rect(screen, ri['color'], pygame.rect.Rect(ri['position'], (h, h)))


class ReetKikker(Entity):
    def __init__(self, color: str, radius: int, position: Vector2, key_bindings: KeyBindings,
                 movement_speed: int):
        super().__init__(color, radius, position, key_bindings, movement_speed)
        self.tongue: Optional[Entity] = None
        self.tong_group = pygame.sprite.Group()

    def update_self(self, dt):
        keys = pygame.key.get_pressed()
        if keys[self.key_binding['up']]:
            self.position.y += self.movement_speed * dt
            self.direction = "up"
        if keys[self.key_binding['right']]:
            self.position.x += self.movement_speed * dt
            self.direction = "right"
        if keys[self.key_binding['down']]:
            self.position.y -= self.movement_speed * dt
            self.direction = "down"
        if keys[self.key_binding['left']]:
            self.position.x -= self.movement_speed * dt
            self.direction = "left"
        if keys[self.key_binding['lick']]:
            p = self.position.copy()
            p.x += self.radius
            p.y += self.radius
            self.tongue = Tongue("red", 5, p, self.key_binding, self.movement_speed * 1.5,
                                 self.tong_group, direction=self.direction)

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
                 movement_speed: int, tongue_group: pygame.sprite.Group, direction="up"):
        super().__init__(color, radius, position, key_bindings, movement_speed, direction=direction)
        self.tongue_group = tongue_group
        self.tongue: Optional[Entity] = None
        self.retracting = bool(pygame.sprite.spritecollideany(self, tongue_group))
        self.add(tongue_group)
        self.direction = direction

    def get_render_information(self) -> Iterable[RenderInformation]:
        own = super().get_render_information()
        return chain(own, self.tongue.get_render_information()) if self.tongue else own

    def update_self(self, dt: int) -> None:
        keys = pygame.key.get_pressed()
        if not keys[self.key_binding['lick']] or self.retracting:  # destruct tongue
            raise TongueInactiveException()
        direction = self.direction
        if keys[self.key_binding['up']]:
            direction = "up"
        elif keys[self.key_binding['right']]:
            direction = "right"
        elif keys[self.key_binding['down']]:
            direction = "down"
        elif keys[self.key_binding['left']]:
            direction = "left"
        nw_position = self.update_position(direction)
        # spawn new tip of tongue
        self.tongue = Tongue(self.color, self.radius, nw_position, self.key_binding, self.movement_speed,
                             self.tongue_group, direction=direction)

    def update_position(self, direction: Direction) -> Vector2:
        nw_position = self.position.copy()
        if direction == "up":
            nw_position.y += self.radius * 2
        elif direction == "right":
            nw_position.x += self.radius * 2
        elif direction == "down":
            nw_position.y -= self.radius * 2
        elif direction == "left":
            nw_position.x -= self.radius * 2
        return nw_position

    def update(self, dt: int) -> None:
        if self.tongue:  # hand over control to tip of tongue
            try:
                self.tongue.update(dt)
            except TongueInactiveException:
                self.tongue = None
                self.retracting = True
        else:
            self.update_self(dt)
