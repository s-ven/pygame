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

MAX_SPEED = 5
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
    b1 = Box(62, 171, 20, 20, RED, 2, -4)
    b2 = Box(90, 60, 65, 65, GREEN, -2, 1)
    b3 = Box(100, 575, 20, 20, BLUE)
    b4 = Box(50, 50, 20, 20, RED)
    b5 = Box(470, 370, 20, 20, YELLOW)
    b6 = Box(300, 550, 30, 30, CHARTREUSE)
    b7 = Box(450, 500, 40, 40, RED)
    b8 = Box(150, 300, 40, 40, YELLOW)
    b9 = Box(350, 100, 40, 40, CHARTREUSE)
    b10 = Box(150, 100, 40, 40, AQUA_MARINE)
    b11 = Box(440, 4, 70, 70, YELLOW)
    b12 = Box(200, 200, 70, 70, CHARTREUSE)
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
        return int(dx_m * self.px_per_m)

    def px_from_speed(self, speed):
        return speed * self.px_per_m

    # Convert from pixels to meters
    def m_from_px(self, px):
        return float(px) / self.px_per_m


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
    def __init__(self, window, sticky_boxes=False, sticky_walls=False, color_transfer=False):
        self.boxes = []
        self.boxCount = len(self.boxes)
        self.color_transfer = color_transfer
        self.boundary = pygame.Rect(0, 0, window.width_px, window.height_px)
        self.window = window
        self.sticky_boxes = sticky_boxes
        self.sticky_walls = sticky_walls

    def draw(self):
        for rect in self.boxes:
            pygame.draw.rect(self.window.surface, rect.color, rect)

    def update(self, dt_s):
        for rect in self.boxes:
            rect.move_box(dt_s)

    def collide(self):
        for i, rect in enumerate(self.boxes):
            rect.collide_playground(self.boundary, self.sticky_walls)
            rect.collide_boxes(self.boxes[i + 1:], self.sticky_boxes)

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

    def __repr__(self):
        return str(vars(self))

    def __neg__(self):
        return Speed(-self.x_mps, -self.y_mps)

    def bounce_y(self):
        self.y_mps = -self.y_mps

    def bounce_x(self):
        self.x_mps = -self.x_mps

    @property
    def abs_x_mps(self):
        return abs(self.x_mps)

    @property
    def abs_y_mps(self):
        return abs(self.y_mps)

    def __add__(self, other):
        return Speed(self.x_mps + other.x_mps, self.y_mps + other.y_mps)

    def __sub__(self, other):
        return Speed(self.x_mps - other.x_mps, self.y_mps - other.y_mps)

    def __mul__(self, other):
        return Speed(self.x_mps * other, self.y_mps * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        return Speed(self.x_mps / other, self.y_mps / other)

    @property
    def coords(self):
        return self.x_mps, self.y_mps


class Box(pygame.Rect):
    """This is a more evolved wrapper around Rect"""

    def __init__(self, x, y, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, color=THECOLORS["aquamarine"], x_mps=None,
                 y_mps=None):
        super().__init__(x, y, width, height)
        self.m_kg = 1.0  # math.log10(width * height)
        self.speed = Speed(x_mps, y_mps)
        self.color = color
        self.links = []

    def __str__(self):
        return str(vars(self)) + ", " + super(Box, self).__str__()

    def link(self, box):
        self.links.append(box)

    def move_box(self, dt_s):
        self.move_m(self.speed, dt_s)

    def move_m(self, speed, dt_s):
        self.move_ip(env.px_from_speed(dt_s * speed).coords)

    def collide_playground(self, playground, sticky_walls):
        if playground.contains(self):
            return
        # Collision with top side
        if self.top <= playground.top:
            self.bounce_y()
            if not sticky_walls:
                self.top = playground.top
        # Collision with bottom side
        if self.bottom >= playground.bottom:
            self.bounce_y()
            if not sticky_walls:
                self.bottom = playground.bottom
        # Collision with left side
        if self.left <= playground.left:
            self.bounce_x()
            if not sticky_walls:
                self.left = playground.left
        # Collision with right side
        if self.right >= playground.right:
            self.bounce_x()
            if not sticky_walls:
                self.right = playground.right

    def collide_boxes(self, boxes, sticky_boxes):
        for box in boxes:
            if self.colliderect(box):
                self.collide_box(box, sticky_boxes)

    def collide_box(self, box, sticky_boxes):
        if playground.color_transfer:
            self.color, box.color = box.color, self.color
        if not sticky_boxes:
            self.fix_penetrations(box)
        else:
            self.speed, box.speed = self.post_collide_speeds(box)

    def post_collide_speeds(self, box, restit_coef=1.0):
        mps = self.m_kg * self.speed + box.m_kg * box.speed
        kg = self.m_kg + self.m_kg
        rel_speed = self.speed - box.speed
        self_speed = (mps - restit_coef * box.m_kg * rel_speed) / kg
        box_speed = (restit_coef * self.m_kg * rel_speed + mps) / kg
        return self_speed, box_speed

    def fix_penetrations(self, box):
        rel_speed = self.speed - box.speed
        penetration_width = env.m_from_px((self.width + box.width) / 2 - abs(self.centerx - box.centerx))
        penetration_height = env.m_from_px((self.height + box.height) / 2 - abs(self.centery - box.centery))

        penetration_ts_x = 0 if rel_speed.x_mps == 0 else penetration_width / rel_speed.abs_x_mps
        penetration_ts_y = 0 if rel_speed.y_mps == 0 else penetration_height / rel_speed.abs_y_mps
        penetration_ts = min(penetration_ts_x, penetration_ts_y)

        # First, back up the two cars, to their collision point, along their incoming trajectory paths.
        # Use BEFORE collision velocities here!
        self.move_m(-self.speed, penetration_ts)
        box.move_m(-box.speed, penetration_ts)

        # Calculate the velocities along the normal AFTER the collision. Use a CR (coefficient of restitution)
        # of 1 here to better avoid stickiness.
        self.speed, box.speed = self.post_collide_speeds(box, restit_coef=1.0)

        # Finally, travel another penetration time worth of distance using these AFTER-collision velocities.
        # This will put the cars where they should have been at the time of collision detection.
        self.move_box(penetration_ts)
        box.move_box(penetration_ts)

    def bounce_y(self):
        self.speed.bounce_y()

    def bounce_x(self):
        self.speed.bounce_x()

    def collide_x(self, box):
        if same_sign(box.speed.x_mps, self.speed.x_mps):
            if not box.speed.abs_x_mps > self.speed.abs_x_mps:
                self.bounce_x()
        else:
            self.bounce_x()

    def collide_y(self, box):
        if same_sign(box.speed.y_mps, self.speed.y_mps):
            if not box.speed.abs_y_mps > self.speed.abs_y_mps:
                self.bounce_y()
        else:
            self.bounce_y()


def main():
    global env, game_window, playground
    pygame.init()
    window_size_px = window_width_px, window_height_px = WINDOW_WIDTH, WINDOW_HEIGHT
    env = Environment(window_width_px, window_height_px, 50)
    game_window = GameWindow(env, window_size_px)
    playground = PlayGround(game_window, False, False, True)
    playground.create_model()
    myclock = pygame.time.Clock()
    framerate_limit = 500
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