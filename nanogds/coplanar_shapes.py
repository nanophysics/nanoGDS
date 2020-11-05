from .base import Shape, Reference
from .shapes import Rectangle

import gdspy
import numpy as np
from copy import deepcopy

PI = np.pi


class CoplanarShape:
    def __init__(self):
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
        self._define_references(shape)
        shape._name = type(self).__name__.upper()
        return shape

    def _draw(self):
        pass

    def _define_references(self, shape):
        pass


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

    def _define_references(self, shape):
        shape.add_reference("CENTER", [0, 0])


# class CoplanarFlexPath(CoplanarShape):
#     def __init__(self, points, width_center, width_gap, radius):
#         super().__init__()
#         center = gdspy.FlexPath(
#             points, width_center, bend_radius=radius, corners="circular bend",
#         )
#         outer = gdspy.FlexPath(
#             points,
#             width_center + 2 * width_gap,
#             bend_radius=radius,
#             corners="circular bend",
#         )
#         ground = gdspy.FlexPath(
#             points,
#             3 * (width_center + 2 * width_gap),
#             bend_radius=radius,
#             corners="circular bend",
#         )
#         self.add_to_center(center)
#         self.add_to_outer(outer)
#         self.add_to_ground(ground)
#         self._draw()


# class CoplanarPath(CoplanarShape):
#     def __init__(self, width_center, width_gap, radius):
#         self._width_center = width_center
#         self._width_gap = width_gap
#         self._radius = radius
#         self._center_path = gdspy.Path(self._width_center)
#         self._outer_path = gdspy.Path(self._width_center + 2 * self._width_gap)
#         self._ground_path = gdspy.Path(3 * (self._width_center + 2 * self._width_gap))
#         self._path_is_empty = True
#         super().__init__()

#     def _draw(self):
#         self.add_to_ground(self._ground_path)
#         self.add_to_outer(self._outer_path)
#         self.add_to_center(self._center_path)
#         if not self._path_is_empty:
#             super()._draw()
#         self.add_reference("END", [self._center_path.x, self._center_path.y])

#     def segment(self, *args, **kwargs):
#         for path in [self._ground_path, self._outer_path, self._center_path]:
#             path.segment(*args, **kwargs)
#         self._path_is_empty = False
#         self._draw()

#     def turn(self, *args, **kwargs):
#         for path in [self._ground_path, self._outer_path, self._center_path]:
#             path.turn(self._radius, *args, **kwargs)
#         self._path_is_empty = False
#         self._draw()

#     @property
#     def length(self):
#         return self._center_path.length


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

    def _define_references(self, shape):
        shape.add_reference("END", [self._length + self._taper_length, 0])

