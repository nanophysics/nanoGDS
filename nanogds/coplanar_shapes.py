from .base import CoplanarShape
from .shapes import Rectangle

import gdspy
import numpy as np
from copy import deepcopy

PI = np.pi


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
        self.add_reference("START", [0, 0])
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
    def __init__(self, width, length, gap, taper_length, taper_width, taper_gap, ground=True):
        self._width = width
        self._length = length
        self._gap = gap
        self._taper_length = taper_length
        self._taper_width = taper_width
        self._taper_gap = taper_gap
        self._ground = ground
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
            self._width + 4 * self._taper_gap,
            self._taper_width + self._taper_gap,
            self._length + 1.5 * self._gap,
            self._taper_length,
        )
        self.add_to_center(path_center)
        self.add_to_outer(path_outer.translate(-self._gap, 0))
        if self._ground:
            self.add_to_ground(path_ground.translate(-1.5 * self._gap, 0))
        self.add_reference("END", [self._length + self._taper_length, 0])


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


class FingerCapacitor(CoplanarShape):
    def __init__(
        self, gap=3, finger_length=10, cpw_width=10, cpw_gap=6, total_length=50
    ):
        self._gap = gap
        self._finger_length = finger_length
        self._cpw_width = cpw_width
        self._cpw_gap = cpw_gap
        self._buffer = (total_length - self._gap - self._finger_length) / 2
        super().__init__()

    def _draw(self):
        self.add_to_ground(
            Rectangle(
                self._finger_length + self._gap + 2 * self._buffer,
                2 * (self._cpw_width + 2 * self._cpw_gap),
            ).translate(0, -self._cpw_width - 2 * self._cpw_gap)
        )
        self.add_to_outer(
            Rectangle(
                self._finger_length + self._gap + 2 * self._buffer,
                self._cpw_width + 2 * self._cpw_gap,
            ).translate(0, -self._cpw_width / 2 - self._cpw_gap)
        )
        if self._buffer > 0:
            self.add_to_center(
                Rectangle(self._buffer, self._cpw_width).translate(0, -self._cpw_width / 2)
            )
            self.add_to_center(
                Rectangle(self._buffer, self._cpw_width).translate(
                    self._buffer + self._finger_length + self._gap, -self._cpw_width / 2
                )
            )
        if self._finger_length > 0:
            self.add_to_center(
                Rectangle(
                    self._finger_length, (self._cpw_width - self._gap) / 2
                ).translate(self._buffer, self._gap / 2)
            )
            self.add_to_center(
                Rectangle(
                    self._finger_length, (self._cpw_width - self._gap) / 2
                ).translate(
                    self._buffer + self._gap,
                    -self._gap / 2 - (self._cpw_width - self._gap) / 2,
                )
            )
        self.add_reference("SIDE 1", [0, 0])
        self.add_reference(
            "SIDE 2", [2 * self._buffer + self._finger_length + self._gap, 0]
        )


class IDFCapacitor(CoplanarShape):
    def __init__(self, w, l, g, n):
        self._w, self._l, self._g, self._n = w, l, g, n
        super().__init__()

    def _draw(self):
        self.add_to_outer(
            Rectangle(self._l + self._g, self._n * self._w + self._n * self._g)
        )
        self.add_to_ground(
            Rectangle(
                self._l + 3 * self._g, self._n * self._w + self._n * self._g
            ).translate(-self._g, 0)
        )
        for i in range(self._n):
            self.add_to_center(
                Rectangle(self._l, self._w).translate(
                    ((i + 1) % 2) * self._g, i * (self._w + self._g)
                )
            )
        self.translate(self._g, 0)
        self.add_reference("BOTTOM", [0, 0])
        self.add_reference("TOP", [0, self._n * self._w + self._n * self._g])


class Inductor(CoplanarShape):
    def __init__(self, w, l, g, n):
        self._w, self._l, self._g, self._n = w, l, 2 * g, n
        super().__init__()

    def _draw(self):
        self.add_to_ground(
            Rectangle(
                2 * (self._l + 3 * self._g), (2 * self._n + 4) * self._g,
            ).translate(-self._l - 2 * self._g, 0)
        )
        self.add_to_outer(
            Rectangle(
                2 * (self._l + 2 * self._g), (2 * self._n + 4) * self._g
            ).translate(-self._l - 2 * self._g, 0)
        )

        path = gdspy.FlexPath([(0, 0)], 2 * self._w)
        path.segment((0, 2 * self._g), width=self._w, relative=True)
        for i in range(self._n):
            path.segment((-self._l, 0), width=self._w, relative=True)
            path.segment((0, self._g), width=self._w, relative=True)
            path.segment((2 * self._l, 0), width=self._w, relative=True)
            path.segment((0, self._g), width=self._w, relative=True)
            path.segment((-self._l, 0), width=self._w, relative=True)
        path.segment((0, 2 * self._g), width=2 * self._w, relative=True)
        self.add_to_center(path)
        self.add_reference("BOTTOM", [0, 0])
        self.add_reference("TOP", [0, (2 * self._n + 4) * self._g])


class LCFilter(CoplanarShape):
    def __init__(self, w, g, l, n_c, n_i):
        self._w, self._g, self._l, self._n_c, self._n_i = w, g, l, n_c, n_i
        super().__init__()

    def _draw(self):
        finger_cap = IDFCapacitor(self._w, self._l, self._g, self._n_c)
        self.combine(finger_cap, add_refs=True)
        self.combine(finger_cap.mirror((0, 1)))
        inductor = Inductor(self._w, self._l, self._g, self._n_i)
        self.combine(
            inductor,
            position=self.points["IDFCAPACITOR TOP"],
            connect_point=inductor.points["BOTTOM"],
            add_refs=True,
        )
