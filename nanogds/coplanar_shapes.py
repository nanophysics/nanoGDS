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
        if self._ground:
            for shape in self._ground:
                self.add(shape)
        if self._outer:
            for shape in self._outer:
                self.add(shape, operation="not")
        if self._center:
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


class CoplanarFlexPath(CoplanarShape):
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


class CoplanarPath(CoplanarShape):
    def __init__(self, width_center, width_gap, radius):
        self._width_center = width_center
        self._width_gap = width_gap
        self._radius = radius
        self._center_path = gdspy.Path(self._width_center)
        self._outer_path = gdspy.Path(self._width_center + 2 * self._width_gap)
        self._ground_path = gdspy.Path(3 * (self._width_center + 2 * self._width_gap))
        self._path_is_empty = True
        super().__init__()

    def _draw(self):
        self.add_to_ground(self._ground_path)
        self.add_to_outer(self._outer_path)
        self.add_to_center(self._center_path)
        if not self._path_is_empty:
            super()._draw()
        self.add_reference("END", [self._center_path.x, self._center_path.y])

    def segment(self, *args, **kwargs):
        for path in [self._ground_path, self._outer_path, self._center_path]:
            path.segment(*args, **kwargs)
        self._path_is_empty = False
        self._draw()

    def turn(self, *args, **kwargs):
        for path in [self._ground_path, self._outer_path, self._center_path]:
            path.turn(self._radius, *args, **kwargs)
        self._path_is_empty = False
        self._draw()

    @property
    def length(self):
        return self._center_path.length
