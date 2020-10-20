from .base import Shape, Reference
from .shapes import Rectangle

import gdspy
import numpy as np

PI = np.pi


class CoplanarShape(Shape):
    def __init__(self):
        self._center = []
        self._outer = []
        self._ground = []
        super().__init__()

    def _draw(self):
        for shape in self._ground:
            self.add(shape)
        for shape in self._outer:
            self.add(shape, operation="not")
        for shape in self._center:
            self.add(shape)

    def add_to_center(self, shape):
        self._center.append(shape)

    def add_to_outer(self, shape):
        self._outer.append(shape)

    def add_to_ground(self, shape):
        self._ground.append(shape)

    def combine(self, shape):
        self._center += shape._center
        self._outer += shape._outer
        self._ground += shape._ground
        self._draw()


class CoplanarPath(CoplanarShape):
    def __init__(self, points, width_center, width_gap, radius):
        super().__init__()
        center = gdspy.FlexPath(
            points, width_center, bend_radius=radius, corners="circular bend",
        )
        outer = gdspy.FlexPath(
            points,
            width_center + 2 * width_gap,
            bend_radius=radius,
            corners="circular bend",
        )
        ground = gdspy.FlexPath(
            points,
            3 * (width_center + 2 * width_gap),
            bend_radius=radius,
            corners="circular bend",
        )
        self.add_to_center(center)
        self.add_to_outer(outer)
        self.add_to_ground(ground)
        self._draw()

