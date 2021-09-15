import pygame
import random
from pygame import gfxdraw


# Star main class
class Stars(object):

    def __init__(self, surf, w, h):
        self._surf = surf
        self.y_cord = h
        self._x = random.randint(0, w)
        self._y = random.randint(0, h)
        self._r = random.randint(0, 1)
        self.starSpeed = random.randint(1, 4)
        self.color = (255, 255, 255)

    def draw(self):
        pygame.gfxdraw.filled_ellipse(self._surf, self._x, self._y, self._r, self._r, self.color)
        print('drawn')

    def move(self):
        self._y += self.starSpeed
        if self._y > self.y_cord:
            self._y = random.randrange(-50, 0)
