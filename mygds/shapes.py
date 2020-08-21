from abc import ABC, abstractmethod

import gdspy
import numpy as np
from .helpers import Reference


class Shape(ABC):
    def __init__(self):
        self._n_elements = 0
        self._reference = Reference()
        self._shape = gdspy.PolygonSet([])
        self._draw()

    def translate(self, dx, dy):
        self._shape.translate(dx, dy)
        self._reference.translate(dx, dy)
        return self

    def rotate(self, radians, center=(0, 0)):
        self._shape.rotate(radians, center)
        self._reference.rotate(radians, center)
        return self

    def scale(self, scalex, scaley=None, center=(0, 0)):
        self._shape.scale(scalex, scaley, center)
        self._reference.scale(scalex, scaley, center)
        return self

    def mirror(self, p1, p2=(0, 0)):
        self._shape.mirror(p1, p2)
        self._reference.mirror(p1, p2)
        return self

    def add(self, element, position=None):
        self._n_elements += 1
        if position is not None:
            element.translate(position[0], position[1])
        self._shape = gdspy.boolean(self._shape, element.shape, "or")

    def add_reference(self, name, point):
        self._reference.add(name, point)

    def _draw(self):
        pass

    @property
    def shape(self):
        return self._shape

    @property
    def polygons(self):
        return self.shape.polygons

    @property
    def points(self):
        return self._reference.points


class Square(Shape):
    def __init__(self, size):
        self._size = size
        super().__init__()

    def _draw(self):
        self._shape = gdspy.Rectangle((0, 0), (self._size, self._size))
        self.add_reference("ORIGIN", (0, 0))
        self.add_reference("TOPRIGHT", (self._size, self._size))


class Rectangle(Shape):
    def __init__(self, sizex, sizey):
        self._sizex = sizex
        self._sizey = sizey
        super().__init__()

    def _draw(self):
        self._shape = gdspy.Rectangle((0, 0), (self._sizex, self._sizey))
        self.add_reference("ORIGIN", (0, 0))
        self.add_reference("TOPRIGHT", (self._sizex, self._sizey))


class Marker(Shape):
    def __init__(self, size):
        self._size = size
        super().__init__()

    def _draw(self):
        self.add(Square(self._size), position=(-self._size, -self._size))
        self.add(Square(self._size))
        self.add_reference("CENTER", (0, 0))


class MarkerField(Shape):
    def __init__(self, size, nx, ny, pitch):
        self._size = size
        self._nx = nx
        self._ny = ny
        self._pitch = pitch
        super().__init__()

    def _draw(self):
        for i in range(self._nx):
            for j in range(self._ny):
                position = (i * self._pitch, j * self._pitch)
                self.add(Marker(self._size), position=position)
                self.add_reference(f"MARKER_{i+1}_{j+1}", position)
