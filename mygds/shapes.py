from abc import ABC, abstractmethod

import gdspy
import numpy as np


class Shape(ABC):
    def __init__(self):
        self._points = {}
        self._shape = gdspy.PolygonSet([])
        self._draw()

    def translate(self, dx, dy):
        self._shape.translate(dx, dy)
        return self

    def rotate(self, angle, center=(0, 0)):
        self._shape.rotate(np.deg2rad(angle), center)
        return self

    def scale(self, scalex, scaley=None, center=(0, 0)):
        self._shape.scale(scalex, scaley, center)
        return self

    def mirror(self, p1, p2=(0, 0)):
        self._shape.mirror(p1, p2)
        return self

    @abstractmethod
    def _get_points(self):
        pass

    @abstractmethod
    def _draw(self):
        pass

    @property
    def shape(self):
        return self._shape

    @property
    def polygon(self):
        return self.shape.polygons[0]

    @property
    def points(self):
        self._get_points()
        return self._points


class Square(Shape):
    def __init__(self, size):
        self._size = size
        super().__init__()

    def _draw(self):
        self._shape = gdspy.Rectangle((0, 0), (self._size, self._size))

    def _get_points(self):
        (
            self._points["ORIGIN"],
            self._points["BOTTOMRIGHT"],
            self._points["TOPRIGHT"],
            self._points["TOPLEFT"],
        ) = self.polygon
        self._points["END"] = self._points["TOPRIGHT"]


class Rectangle(Shape):
    def __init__(self, sizex, sizey):
        self._sizex = sizex
        self._sizey = sizey
        super().__init__()

    def _draw(self):
        self._shape = gdspy.Rectangle((0, 0), (self._sizex, self._sizey))

    def _get_points(self):
        (
            self._points["ORIGIN"],
            self._points["BOTTOMRIGHT"],
            self._points["TOPRIGHT"],
            self._points["TOPLEFT"],
        ) = self.polygon
        self._points["END"] = self._points["TOPRIGHT"]

