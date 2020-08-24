from .base import Shape, Reference

import gdspy
import numpy as np

PI = np.pi


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


class Cross(Shape):
    def __init__(self, size, width):
        self._size = size
        self._width = width
        super().__init__()

    def _draw(self):
        w = self._width
        l = self._size
        self.add(gdspy.Rectangle((-l / 2, -w / 2), (l / 2, w / 2)))
        self.add(gdspy.Rectangle((-w / 2, -l / 2), (w / 2, l / 2)))
        self.add_reference("CENTER", (0, 0))


class Marker(Shape):
    def __init__(self, size):
        self._size = size
        super().__init__()

    def _draw(self):
        self.add(Square(self._size), position=(-self._size, -self._size))
        self.add(Square(self._size))
        self.add_reference("CENTER", (0, 0))


class MarkerField(Shape):
    def __init__(self, size, nx, ny, pitch, label=False):
        self._size = size
        self._nx = nx
        self._ny = ny
        self._pitch = pitch
        self._with_label = label
        super().__init__()

    def _draw(self):
        for i in range(self._nx):
            for j in range(self._ny):
                position = (i * self._pitch, j * self._pitch)
                self.add(Marker(self._size), position=position)
                self.add_reference(f"MARKER_{i+1}_{j+1}", position)
                if self._with_label:
                    self.add(
                        gdspy.Text(
                            f"{i+1}",
                            2 * self._size,
                            position=(position[0] - 1.5 * self._size, position[1]),
                        )
                    )
                    if j != i:
                        self.add(
                            gdspy.Text(
                                f"{j+1}",
                                2 * self._size,
                                position=(
                                    position[0] + 0.5 * self._size,
                                    position[1] - 2.5 * self._size,
                                ),
                            )
                        )

    def add_corners(self):
        angle = Shape()
        angle.add(
            Rectangle(self._size, 4 * self._size), position=(self._size, self._size)
        )
        angle.add(
            Rectangle(4 * self._size, self._size), position=(self._size, self._size)
        )
        cross = Shape()
        for i in range(4):
            cross.add(angle.rotate(i * PI / 2))

        corners = [(1, 1), (1, self._nx), (self._nx, self._ny), (self._nx, 1)]
        for i, j in corners:
            self.add(cross, position=self.points[f"MARKER_{i}_{j}"])


class Bondpad(Shape):
    def __init__(self, width, height):
        self._width = width
        self._height = height
        super().__init__()

    def _draw(self):
        w = self._width
        h = self._height
        self.add(gdspy.Rectangle([-w / 2, -h / 2], [w / 2, h / 2]))
        self.add_reference("CONNECTION", [0, h / 2])


class BondpadRow(Shape):
    def __init__(self, positions, pad_width=200, pad_height=300):
        self._positions = positions
        self._pad_width = pad_width
        self._pad_height = pad_height
        super().__init__()

    def _draw(self):
        for i, x in enumerate(self._positions):
            bondpad = Bondpad(self._pad_width, self._pad_height)
            self.add(bondpad, position=[x, 0], add_refs=True, counter=i + 1)


class Lead(Shape):
    def __init__(self, points, widths):
        if len(points) < 2:
            raise Exception("Specify at least 2 points.")
        self._path = points
        self._widths = widths
        super().__init__()

    def _draw(self):
        path = gdspy.FlexPath([self._path[0]], self._widths[0], ends="extended")
        for p, w in zip(self._path[1:], self._widths[1:]):
            path.segment(p, width=w)
        self.add(path)
        self.add_reference("START", self._path[0])
        self.add_reference("END", self._path[-1])


class LeadRow(Shape):
    def __init__(self, point_list, widths):
        self._point_list = point_list
        self._widths = widths
        super().__init__()

    def _draw(self):
        n_leads = len(self._point_list[0])
        for i in range(n_leads):
            points = []
            for lst in self._point_list:
                points.append(lst[i])
            lead = Lead(points, self._widths)
            self.add(lead)

