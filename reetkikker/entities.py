from typing import Callable, Protocol, TypedDict, Optional, Literal, Any, Tuple
from pygame import Surface, Vector2
import pygame
from pygame.sprite import Sprite, Group

Size = Tuple[int, int]
Direction = Optional[Literal["up", "right", "down", "left"]]
renderer = Callable[[Any, Surface], None]


class TongueInactiveException(Exception):
    pass


class KeyBindings(TypedDict):
    up: int
    right: int
    down: int
    left: int
    lick: int


DIRECTION_COEFFICIENTS = {
    "up": (-1, 0),
    "right": (0, 1),
    "down": (1, 0),
    "left": (0, -1)

}


class Renderable(Protocol):

    def render(self, screen: Surface) -> None:
        pass


class Updatable(Protocol):
    def update(self, dt: int) -> None:
        pass


# most basic renderer
def entity_renderer(e: "Entity", screen: Surface):
    h = 2 * e.radius
    pygame.draw.rect(screen, e.color, pygame.rect.Rect(e.position, (h, h)))


# the reetkikker renderer takes recursively care of the tongue members
def reetkikker_renderer(e: "ReetKikker", screen: Surface):
    if e.tongue:
        e.tongue.render(screen)
    rotation = {
        "up": 0,
        "right": -90,
        "down": 180,
        "left": 90

    }
    scaled = pygame.transform.scale(e.image, e.size)
    rotated = pygame.transform.rotate(scaled, rotation[e.direction])
    screen.blit(rotated, e.position)


def tongue_renderer(t: "Tongue", screen: Surface):
    if t.tongue:
        t.tongue.render(screen)
    entity_renderer(t, screen)


class Entity(Sprite, Updatable, Renderable):
    image: Surface

    def __init__(self, position: Vector2, size: Size, key_bindings: KeyBindings,
                 movement_speed: int, direction=None, renderer: renderer = entity_renderer):
        super().__init__()
        self.position = position
        self.size = size
        self.key_binding = key_bindings
        self.movement_speed = movement_speed
        self.direction: Direction = direction or "up"
        self.renderer = renderer

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.position, self.size)

    def update(self, dt: int) -> None:
        pass

    def render(self, screen: Surface) -> None:
        self.renderer(self, screen)


class ReetKikker(Entity):
    image = pygame.image.load("assets/reetkikker.gif")

    def __init__(self, position: Vector2, size: Size, key_bindings: KeyBindings,
                 movement_speed: int, direction="up", renderer=reetkikker_renderer):
        super().__init__(position, size, key_bindings, movement_speed, direction, renderer)
        self.tongue: Optional[Entity] = None
        self.tong_group: Group = Group()

    def update_self(self, dt):
        keys = pygame.key.get_pressed()
        # check if tongue is 'spawned'. Don't move if so
        if keys[self.key_binding['lick']]:  # spawn tongue
            p = self.position.copy()
            p.x += (self.size[0] // 2) - 4  # half tongue size
            p.y += (self.size[1] // 2) - 4
            self.tongue = Tongue(p, (9, 9), self.key_binding, self.movement_speed * 2,
                                 self.tong_group, direction=self.direction)
            return
        # No lick condition --> check if we need to move
        yc, xc = None, None
        # first check if current direction is still 'selected'
        if keys[self.key_binding[self.direction]]:  # type: ignore
            yc, xc = DIRECTION_COEFFICIENTS[self.direction]
        # else, check remaining direction
        else:
            for direction in {'up', 'right', 'down', 'left'} - {self.direction}:
                if keys[self.key_binding[direction]]:
                    yc, xc = DIRECTION_COEFFICIENTS[direction]
                    self.direction = direction
                    break
        # make the move
        if yc is not None and xc is not None:
            self.position.x += xc * self.movement_speed * dt
            self.position.y += yc * self.movement_speed * dt

    def update_tongue(self, dt):
        try:
            self.tongue.update(dt)
        except TongueInactiveException:
            self.tongue = None
            self.tong_group = Group()

    def update(self, dt):
        if self.tongue:
            self.update_tongue(dt)
        else:
            self.update_self(dt)


class Tongue(Entity):
    image = pygame.image.load("assets/tongue.png")

    def __init__(self, position: Vector2, size: Size, key_bindings: KeyBindings,
                 movement_speed: int, tongue_group: pygame.sprite.Group, direction="up", renderer=reetkikker_renderer):
        super().__init__(position, size, key_bindings, movement_speed, direction=direction, renderer=renderer)
        self.tongue_group = tongue_group
        self.tongue: Optional[Entity] = None
        self.retracting = bool(pygame.sprite.spritecollideany(self, tongue_group))  # type: ignore
        self.add(tongue_group)
        self.direction = direction

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
        nw_position = self.update_position(direction)  # type: ignore
        # spawn new tip of tongue
        self.tongue = Tongue(nw_position, self.size, self.key_binding, self.movement_speed,
                             self.tongue_group, direction=direction)

    def update_position(self, direction: Direction) -> Vector2:
        nw_position = self.position.copy()
        w, h = self.size
        yc, xc = DIRECTION_COEFFICIENTS[direction]
        nw_position.x += xc * w
        nw_position.y += yc * h
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
