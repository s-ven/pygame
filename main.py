import random
import sys

import pygame
from pygame.color import THECOLORS
from pygame.locals import *

# set up pygame

# set up the window
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
PX_PER_M = 1

MAX_SPEED = 3
DEFAULT_WIDTH = 10
DEFAULT_HEIGHT = 10

pygame.display.set_caption("Animation")

# set up colors
BLACK = THECOLORS["black"]
AQUA_MARINE = THECOLORS["aquamarine"]
YELLOW = THECOLORS["yellow"]
CHARTREUSE = THECOLORS["chartreuse"]
RED = THECOLORS["red"]
GREEN = THECOLORS["green"]
BLUE = THECOLORS["blue"]


# set up the block data structure
def make_random_boxes():
    b1 = Box(64, 167, 20, 20, RED, 2, -4)
    b2 = Box(88, 61, 100, 100, GREEN, -2, 1)
    b3 = Box(100, 575, 20, 45, BLUE)
    b4 = Box(50, 50, 20, 20, RED)
    b5 = Box(470, 370, 20, 20, YELLOW)
    b6 = Box(300, 550, 30, 30, CHARTREUSE)
    b7 = Box(450, 500, 40, 40, RED)
    b8 = Box(150, 300, 40, 40, YELLOW)
    b9 = Box(350, 100, 40, 40, CHARTREUSE)
    b10 = Box(150, 100, 40, 40, AQUA_MARINE)
    b11 = Box(440, 4, 100, 100, YELLOW)
    b12 = Box(200, 200, 100, 100, CHARTREUSE)
    b13 = Box(400, 150, 60, 60, AQUA_MARINE)
    b14 = Box(150, 350, 20, 20, RED)
    b15 = Box(150, 450, 20, 20, YELLOW)
    b16 = Box(300, 50, 30, 30, CHARTREUSE)
    b17 = Box(450, 400, 40, 40, RED)
    b18 = Box(250, 200, 40, 40, YELLOW)
    b19 = Box(150, 300, 40, 40, CHARTREUSE)
    b20 = Box(350, 100, 40, 40, AQUA_MARINE)
    return [b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12, b13, b14, b15, b16, b17, b18, b19, b20]


class Environment:
    def __init__(self, width_px=WINDOW_WIDTH, height_px=WINDOW_HEIGHT, px_per_m=PX_PER_M):
        self.px_per_m = px_per_m
        self.width_px = width_px
        self.height_px = height_px
        self.width_m = float(width_px) / px_per_m
        self.height_m = float(height_px) / px_per_m

    # Convert from meters to pixels
    def px_from_m(self, dx_m):
        return int(round(dx_m * self.px_per_m))

    # Convert from pixels to meters
    def m_from_px(self, dx_px):
        return float(dx_px) / self.px_per_m


class GameWindow:
    def __init__(self, env, screen_tuple_px, title=None):
        self.width_px = screen_tuple_px[0]
        self.height_px = screen_tuple_px[1]

        # Create a reference to display's surface object. This object is a pygame "surface".
        # Screen dimensions in pixels (tuple)
        self.surface = pygame.display.set_mode(screen_tuple_px)

        # Define the physics-world boundaries of the window.
        self.left_m = 0.0
        self.right_m = env.m_from_px(self.width_px)
        self.top_m = 0.0
        self.bottom_m = env.m_from_px(self.height_px)

        # Paint screen black.
        self.erase_and_update()
        self.caption = title

    def update_caption(self, title):
        pygame.display.set_caption(title)
        self.caption = title

    def erase_and_update(self):
        # Useful for shifting between the various demos.
        self.surface.fill(THECOLORS["black"])
        pygame.display.flip()


class PlayGround:
    def __init__(self, window):
        self.boxes = []
        self.boxCount = len(self.boxes)
        self.color_transfer = False
        self.boundary = pygame.Rect(0, 0, window.width_px, window.height_px)
        self.window = window

    def draw(self):
        for rect in self.boxes:
            pygame.draw.rect(self.window.surface, rect.color, rect)

    def update(self, dt_s):
        for rect in self.boxes:
            rect.move_box(dt_s)

    def collide(self):
        for rect in self.boxes:
            rect.collide_playground(self.boundary)
        for i, rect in enumerate(self.boxes):
            rect.collide_boxes(self.boxes)

    def create_model(self):
        self.boxes = make_random_boxes()


def same_sign(x, y):
    return (x >= 0 and y >= 0) or (x < 0 and y < 0)


def random_speed(speed):
    if speed is None:
        return random.randrange(-MAX_SPEED, MAX_SPEED)
    return speed


class Speed:
    def __init__(self, x_mps=None, y_mps=None):
        self.x_mps = random_speed(x_mps)
        self.y_mps = random_speed(y_mps)
        self._tmp_speed = None
        self._next_speed = None

    def __repr__(self):
        return str(vars(self))

    def bounce(self):
        self._next_speed = Speed(-self.x_mps, -self.y_mps)

    def bounce_y(self):
        self._next_speed = Speed(self.x_mps, -self.y_mps)

    def bounce_x(self):
        self._next_speed = Speed(-self.x_mps, self.y_mps)

    def append(self, x=None, y=None):
        self._tmp_speed = None if x is None and y is None else Speed(x, y)

    @property
    def abs_x_mps(self):
        return abs(self.x_mps)

    @property
    def abs_y_mps(self):
        return abs(self.y_mps)

    @property
    def coords(self):
        if self._next_speed is not None:
            self.x_mps = self._next_speed.x_mps
            self.y_mps = self._next_speed.y_mps
            self._next_speed = None
        speed = self
        if self._tmp_speed is not None:
            speed = Speed(speed.x_mps + self._tmp_speed.x_mps, speed.y_mps + self._tmp_speed.y_mps)
            self._tmp_speed = None

        return speed.x_mps, speed.y_mps

    @property
    def next_coords(self):
        speed = self
        if self._next_speed is not None:
            self.x_mps = self._next_speed.x_mps
            self.y_mps = self._next_speed.y_mps
        if self._tmp_speed is not None:
            speed = Speed(speed.x_mps + self._tmp_speed.x_mps, speed.y_mps + self._tmp_speed.y_mps)

        return speed.x_mps, speed.y_mps


class Box(pygame.Rect):
    """This is a more evolved wrapper around Rect"""

    def __init__(self, x, y, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, color=THECOLORS["aquamarine"], x_mps=None,
                 y_mps=None):
        super().__init__(x, y, width, height)
        self.speed = Speed(x_mps, y_mps)
        self.color = color
        self.links = []

    def __str__(self):
        return str(vars(self)) + ", " + super(Box, self).__str__()

    def link(self, box):
        self.links.append(box)

    def move_box(self, dt_s):
        x, y = self.speed.coords

        links_nb = len(self.links)
        if links_nb > 0:
            center_x, center_y = None, None
            for box in self.links:
                center_x += box.centerx
                center_y += box.centery
            center_x /= links_nb
            center_y /= links_nb

        self.move_ip(env.px_from_m(x * dt_s), env.px_from_m(y * dt_s))

    def collide_playground(self, playground):
        if playground.contains(self):
            return
        # Collision with top side
        if self.collidepoint(self.left, playground.top):
            self.bounce_y()
            self.speed.append(0, playground.top - self.top)
        # Collision with bottom side
        if self.collidepoint(self.left, playground.bottom):
            self.bounce_y()
            self.speed.append(0, playground.bottom - self.bottom)
        # Collision with left side
        if self.collidepoint(playground.left, self.top):
            self.bounce_x()
            self.speed.append(playground.left - self.left, 0)
        # Collision with right side
        if self.collidepoint(playground.right, self.top):
            self.bounce_x()
            self.speed.append(playground.right - self.right, 0)

    def collide_boxes(self, boxes):
        for box in boxes:
            if box == self:
                continue
            if self.colliderect(box):
                self.collide_box(box)

    def collide_box(self, box):
        dy = 0.5 * (self.centery - box.centery)
        dx = 0.5 * (self.centerx - box.centerx)
        if dx == 0.0:
            self.collide_y(box)
            return
        if dy == 0.0:
            self.collide_x(box)
            return

        w = self.width + box.width
        h = self.height + box.height
        wy = w * dy
        hx = h * dx
        if wy > hx:
            if wy > -hx:
                self.collide_y(box)
            else:
                self.collide_x(box)
        else:
            if wy > -hx:
                self.collide_x(box)
            else:
                self.collide_y(box)

    def bounce_y(self):
        self.speed.bounce_y()

    def bounce_x(self):
        self.speed.bounce_x()

    def collide_x(self, box):
        if same_sign(box.speed.x_mps, self.speed.x_mps):
            if not box.speed.abs_x_mps > self.speed.abs_x_mps:
                self.bounce_x()
        else:
            if self.speed.abs_x_mps + box.speed.abs_x_mps != 0:
                h = self.clip(box).width / (self.speed.abs_x_mps + box.speed.abs_x_mps) * self.speed.x_mps
                self.speed.append(-h, 0)
            self.bounce_x()

    def collide_y(self, box):
        if same_sign(box.speed.y_mps, self.speed.y_mps):
            if not box.speed.abs_y_mps > self.speed.abs_y_mps:
                self.bounce_y()
        else:
            if self.speed.abs_y_mps + box.speed.abs_y_mps != 0:
                h = self.clip(box).height / (self.speed.abs_y_mps + box.speed.abs_y_mps) * self.speed.y_mps
                self.speed.append(0, -h)
            self.bounce_y()


def main():
    global env
    pygame.init()
    window_size_px = window_width_px, window_height_px = WINDOW_WIDTH, WINDOW_HEIGHT
    env = Environment(window_width_px, window_height_px, 50)
    game_window = GameWindow(env, window_size_px)
    playground = PlayGround(game_window)
    playground.create_model()
    myclock = pygame.time.Clock()
    framerate_limit = 400
    while True:
        game_window.surface.fill(BLACK)
        dt_s = float(myclock.tick(framerate_limit) * 1e-3)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        playground.update(dt_s)
        playground.collide()
        playground.draw()

        pygame.display.flip()


main()
