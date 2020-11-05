from .base import CoplanarShape
from .shapes import Rectangle

import gdspy
import numpy as np
from copy import deepcopy

PI = np.pi


class RectangleCapacitor(CoplanarShape):
    def __init__(self, x, y, gap):
        self._x, self._y = x, y
        self._gap = gap
        super().__init__()

    def _draw(self):
        x1, y1 = self._x, self._y
        x2, y2 = self._x + 2 * self._gap, self._y + 2 * self._gap
        x3, y3 = self._x + 3 * self._gap, self._y + 3 * self._gap

        self.add_to_center(Rectangle(x1, y1).translate(-x1 / 2, -y1 / 2))
        self.add_to_outer(Rectangle(x2, y2).translate(-x2 / 2, -y2 / 2))
        self.add_to_ground(Rectangle(x3, y3).translate(-x3 / 2, -y3 / 2))
        self.add_reference("CENTER", [0, 0])


class CoplanarPath(CoplanarShape):
    def __init__(self, width_center, width_gap, radius):
        self._width_center = width_center
        self._width_gap = width_gap
        self._radius = radius
        super().__init__()

    def _draw(self):
        self.add_to_center(gdspy.Path(self._width_center))
        self.add_to_outer(gdspy.Path(self._width_center + 2 * self._width_gap))
        self.add_to_ground(gdspy.Path(3 * (self._width_center + 2 * self._width_gap)))
        self.add_reference("END", [self._center[0].x, self._center[0].y])

    def segment(self, *args, **kwargs):
        for path in [self._ground[0], self._outer[0], self._center[0]]:
            path.segment(*args, **kwargs)
        self.add_reference("END", [self._center[0].x, self._center[0].y])

    def turn(self, *args, **kwargs):
        for path in [self._ground[0], self._outer[0], self._center[0]]:
            path.turn(self._radius, *args, **kwargs)
        self.add_reference("END", [self._center[0].x, self._center[0].y])

    @property
    def length(self):
        return self._center[0].length


class Bondpad(CoplanarShape):
    def __init__(self, width, length, gap, taper_length, taper_width, taper_gap):
        self._width = width
        self._length = length
        self._gap = gap
        self._taper_length = taper_length
        self._taper_width = taper_width
        self._taper_gap = taper_gap
        super().__init__()

    def _get_path(self, w1, w2, l1, l2):
        path = gdspy.Path(w1)
        path.segment(l1, final_width=w1)
        path.segment(l2, final_width=w2)
        return path

    def _draw(self):
        path_center = self._get_path(
            self._width, self._taper_width, self._length, self._taper_length
        )
        path_outer = self._get_path(
            self._width + 2 * self._gap,
            self._taper_width + 2 * self._taper_gap,
            self._length + self._gap,
            self._taper_length,
        )
        path_ground = self._get_path(
            self._width + 6 * self._gap,
            self._taper_width + 6 * self._taper_gap,
            self._length + 3 * self._gap,
            self._taper_length,
        )
        self.add_to_center(path_center)
        self.add_to_outer(path_outer.translate(-self._gap, 0))
        self.add_to_ground(path_ground.translate(-3 * self._gap, 0))
        self.add_reference("END", [self._length + self._taper_length, 0])

