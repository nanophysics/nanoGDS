import nanogds
from .base import Shape, Reference

import gdspy
import numpy as np

PI = np.pi


class Circle(Shape):
    def __init__(self, radius, layer=0):
        self._radius = radius
        self._layer = layer
        super().__init__()

    def _draw(self):
        self.add(
            gdspy.Round((0, 0), (self._radius)), layer=self._layer,
        )
        self.add_reference("CENTER", (0, 0))
        

class Square(Shape):
    def __init__(self, size, layer=0):
        self._size = size
        self._layer = layer
        super().__init__()

    def _draw(self):
        self.add(
            gdspy.Rectangle((0, 0), (self._size, self._size)), layer=self._layer,
        )
        self.add_reference("ORIGIN", (0, 0))
        self.add_reference("TOPRIGHT", (self._size, self._size))


class Rectangle(Shape):
    def __init__(self, sizex, sizey, layer=0):
        self._sizex = sizex
        self._sizey = sizey
        self._layer = layer
        super().__init__()

    def _draw(self):
        self.add(
            gdspy.Rectangle((0, 0), (self._sizex, self._sizey)), layer=self._layer,
        )
        self.add_reference("ORIGIN", (0, 0))
        self.add_reference("TOPRIGHT", (self._sizex, self._sizey))


class Cross(Shape):
    def __init__(self, size, width, layer=0, correction=0):
        self._size = size
        self._width = width
        self._layer = layer
        self._correction = correction
        super().__init__()

    def _draw(self):
        w = self._width
        l = self._size
        self.add(
            gdspy.Rectangle((-l / 2, -w / 2), (l / 2, w / 2)), layer=self._layer,
        )
        self.add(
            gdspy.Rectangle((-w / 2, -l / 2), (w / 2, l / 2)), layer=self._layer,
        )
        self.add_reference("CENTER", (0, 0))
        if self._correction:
            square = Square(self._correction, layer=self._layer).translate(
                -self._correction / 2, -self._correction / 2
            )
            positions = [
                (-l / 2, -w / 2),
                (-l / 2, +w / 2),
                (+l / 2, +w / 2),
                (+l / 2, -w / 2),
                (-l / 2, -w / 2),
                (-w / 2, -w / 2),
                (-w / 2, +l / 2),
                (+w / 2, +l / 2),
                (+w / 2, -l / 2),
                (-w / 2, -l / 2),
            ]
            for p in positions:
                self.add(square, position=p)
            positions = [
                (-w / 2, -w / 2),
                (-w / 2, +w / 2),
                (+w / 2, +w / 2),
                (+w / 2, -w / 2),
            ]
            for p in positions:
                self.add(square, position=p, operation="not")


class Wedge(Shape):
    def __init__(self, width, length, layer=0):
        self._width = width
        self._length = length
        self._layer = layer
        super().__init__()

    def _draw(self):
        w = self._width
        l = self._length
        self.add(gdspy.Polygon([(0, 0), (l, w / 2), (l, -w / 2)], layer=self._layer))


class WedgeMarker(Shape):
    def __init__(self, width, length, correction=0, layer=0):
        self._width = width
        self._length = length
        self._correction = correction
        self._layer = layer
        super().__init__()

    def _draw(self):
        w = self._width
        l = self._length
        c = self._correction
        self.add(nanogds.Wedge(w, l, layer=self._layer), angle=0, layer=self._layer)
        self.add(
            nanogds.Wedge(w, l, layer=self._layer), angle=PI / 2, layer=self._layer
        )
        self.add(
            nanogds.Wedge(w, l, layer=self._layer), angle=-PI / 2, layer=self._layer
        )
        self.add(nanogds.Wedge(w, l, layer=self._layer), angle=PI, layer=self._layer)
        if c:
            self.add(nanogds.Square(c), position=(-c / 2, -c / 2), operation="not")


class Marker(Shape):
    def __init__(self, size, layer=0, correction=0):
        self._size = size
        self._layer = layer
        self._correction = correction
        super().__init__()

    def _draw(self):
        self.add(
            Square(self._size, layer=self._layer), position=(-self._size, -self._size),
        )
        self.add(Square(self._size, layer=self._layer))
        if self._correction:
            square = Square(self._correction, layer=self._layer).translate(
                -self._correction / 2, -self._correction / 2
            )
            positions = [
                (-self._size, 0),
                (-self._size, -self._size),
                (self._size, 0),
                (self._size, self._size),
                (0, self._size),
                (0, -self._size),
            ]
            for p in positions:
                self.add(square, position=p)
        self.add_reference("CENTER", (0, 0))


class Angle(Shape):
    def __init__(self, width, length, layer=0, correction=0):
        self._width = width
        self._length = length
        self._layer = layer
        self._correction = correction
        super().__init__()

    def _draw(self):
        self.add(Rectangle(self._width, self._length, layer=self._layer))
        self.add(Rectangle(self._length, self._width, layer=self._layer))
        if self._correction:
            square = Square(self._correction, layer=self._layer).translate(
                -self._correction / 2, -self._correction / 2
            )
            positions = [
                (0, 0),
                (self._length, 0),
                (0, self._length),
                (self._width, self._length),
                (self._length, self._width),
            ]
            for p in positions:
                self.add(square, position=p)
            self.add(square, position=(self._width, self._width), operation="not")
        self.add_reference("CENTER", (0, 0))


class MarkerField(Shape):
    def __init__(
        self, size, nx, ny, pitch, pitchy=None, correction=0, label=False, layer=0
    ):
        self._size = size
        self._nx = nx
        self._ny = ny
        self._pitch = pitch
        self._pitchy = pitch if pitchy is None else pitchy
        self._with_label = label
        self._layer = layer
        self._correction = correction
        super().__init__()

    def _draw(self):
        for i in range(self._nx):
            for j in range(self._ny):
                position = (i * self._pitch, j * self._pitchy)
                self.add(
                    Marker(self._size, layer=self._layer, correction=self._correction),
                    position=position,
                )
                self.add_reference(f"MARKER_{i+1}_{j+1}", position)
                if self._with_label:
                    self.add(
                        gdspy.Text(
                            f"{i+1}",
                            2 * self._size,
                            position=(position[0] - 1.5 * self._size, position[1]),
                        ),
                        layer=self._layer,
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
                            ),
                            layer=self._layer,
                        )

    def add_corners(self):
        angle = Shape()
        angle.add(
            Rectangle(self._size, 4 * self._size, layer=self._layer),
            position=(self._size, self._size),
        )
        angle.add(
            Rectangle(4 * self._size, self._size, layer=self._layer),
            position=(self._size, self._size),
        )
        cross = Shape()
        for i in range(4):
            cross.add(angle.rotate(i * PI / 2))
        corners = [(1, 1), (1, self._nx), (self._nx, self._ny), (self._nx, 1)]
        for i, j in corners:
            self.add(cross, position=self.points[f"MARKER_{i}_{j}"])

    def add_connection_points(self, n, side="bottom"):
        gridx = np.linspace(0, self._pitch * (self._nx - 1), n + 2)[1:-1]
        gridy = np.linspace(0, self._pitch * (self._ny - 1), n + 2)[1:-1]
        if side == "bottom":
            points = [(x, 0) for x in gridx]
        elif side == "right":
            points = [(self._size, y) for y in gridy]
        elif side == "top":
            points = [(x, self._size) for x in np.flip(gridx)]
        elif side == "left":
            points = [(0, y) for y in np.flip(gridy)]
        else:
            raise Exception()
        [self.add_reference(f"{side.upper()} #{i+1}", p) for i, p in enumerate(points)]


class BondpadShape(Shape):
    def __init__(self, width, height, layer=0):
        self._width = width
        self._height = height
        self._layer = layer
        super().__init__()

    def _draw(self):
        w = self._width
        h = self._height
        self.add(
            gdspy.Rectangle([-w / 2, -h / 2], [w / 2, h / 2]), layer=self._layer,
        )
        self.add_reference("CONNECTION", [0, h / 2])


class BondpadRow(Shape):
    def __init__(self, positions, pad_width=200, pad_height=300, layer=0):
        self._positions = positions
        self._pad_width = pad_width
        self._pad_height = pad_height
        self._layer = layer
        super().__init__()

    def _draw(self):
        for i, x in enumerate(self._positions):
            bondpad = BondpadShape(self._pad_width, self._pad_height, layer=self._layer)
            self.add(
                bondpad, position=[x, 0], add_refs=True, counter=i + 1,
            )


class Lead(Shape):
    def __init__(self, points, widths, layer=0, layer_bondpad=1):
        if len(points) < 2:
            raise Exception("Specify at least 2 points.")
        self._path = points
        self._widths = widths
        self._layer = layer
        self._layer_bondpad = layer_bondpad
        super().__init__()

    def _draw(self):
        # first layer
        path = gdspy.FlexPath([self._path[0]], self._widths[0])
        for p, w in zip(self._path[1:], self._widths[1:]):
            path.segment(p, width=w)
        self.add(path, layer=self._layer)
        # add second layer for thicker bondpads
        path = gdspy.FlexPath([self._path[0]], self._widths[0] - 10)
        for p, w in zip(self._path[1:3], self._widths[1:3]):
            path.segment(p, width=w - 10)
        self.add(path, layer=self._layer_bondpad)
        # add references
        self.add_reference("START", self._path[0])
        self.add_reference("END", self._path[-1])


class LeadRow(Shape):
    def __init__(self, point_list, widths, layer=0, layer_bondpad=1):
        self._point_list = point_list
        self._widths = widths
        self._layer = layer
        self._layer_bondpad = layer_bondpad
        super().__init__()

    def _draw(self):
        n_leads = len(self._point_list[0])
        for i in range(n_leads):
            points = []
            for lst in self._point_list:
                points.append(lst[i])
            lead = Lead(
                points,
                self._widths,
                layer=self._layer,
                layer_bondpad=self._layer_bondpad,
            )
            self.add(lead)

