import gdspy
import numpy as np
from copy import deepcopy

from .shape import Shape
from .reference import Reference


class CoplanarShape:
    def __init__(self):
        self._reference = Reference()
        self.add_reference("ORIGIN", [0, 0])
        self._center = []
        self._outer = []
        self._ground = []
        self._draw()

    def add_to_center(self, shape):
        self._center.append(shape)

    def add_to_outer(self, shape):
        self._outer.append(shape)

    def add_to_ground(self, shape):
        self._ground.append(shape)

    def get_shape(self):
        shape = Shape()
        if self._ground:
            for s in self._ground:
                shape.add(s)
        if self._outer:
            for s in self._outer:
                shape.add(s, operation="not")
        if self._center:
            for s in self._center:
                shape.add(s)
        return shape

    def combine(
        self, shape, position=[0, 0], connect_point=[0, 0], add_refs=False, counter=None
    ):
        shape = deepcopy(shape)
        shape.translate(position[0] - connect_point[0], position[1] - connect_point[1])
        self._center += shape._center
        self._outer += shape._outer
        self._ground += shape._ground
        if add_refs:
            self._merge_references(shape, counter)

    def translate(self, dx, dy):
        for lst in [self._center, self._outer, self._ground]:
            for s in lst:
                s.translate(dx, dy)
        self._reference.translate(dx, dy)
        return self

    def rotate(self, radians, center=(0, 0)):
        for lst in [self._center, self._outer, self._ground]:
            for s in lst:
                s.rotate(radians, center)
        self._reference.rotate(radians, center)
        return self

    def scale(self, scalex, scaley=None, center=(0, 0)):
        for lst in [self._center, self._outer, self._ground]:
            for s in lst:
                s.scale(scalex, scaley, center)
        self._reference.scale(scalex, scaley, center)
        return self

    def mirror(self, p1, p2=(0, 0)):
        for lst in [self._center, self._outer, self._ground]:
            for s in lst:
                s.mirror(p1, p2)
        self._reference.mirror(p1, p2)
        return self

    def _merge_references(self, element, counter):
        for name, point in element.points.items():
            if name == "ORIGIN":
                continue
            new_name = type(element).__name__.upper()
            if counter is not None:
                new_name += f" #{counter}"
            new_name += f" {name}"
            self.add_reference(new_name, point)

    def add_reference(self, name, point):
        self._reference.add(name, point)

    def _draw(self):
        pass

    @property
    def points(self):
        return self._reference.points
