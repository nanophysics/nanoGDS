from abc import ABC, abstractmethod
import gdspy
import numpy as np

from shapes import Shape, Square


class CombinedShape:
    def __init__(self):
        self._n_elements = 0
        self._points = {"ORIGIN": (0, 0), "END": (0, 0)}
        self._shape = gdspy.PolygonSet([])

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

    def add(self, element, position="END", add_points=True):
        self._n_elements += 1
        point = self.points[position]
        element.translate(point[0], point[1])
        self._shape = gdspy.boolean(self._shape, element.shape, "or")
        if add_points:
            self._add_points(element.points)

    def _add_points(self, points):
        for key in points.keys():
            if key == "END":
                self._points[key] = points[key]
            else:
                self._points[f"{key}_{self._n_elements}"] = points[key]

    def _get_points(self):
        pass

    @property
    def shape(self):
        return self._shape

    @property
    def polygons(self):
        return self.shape.polygons

    @property
    def points(self):
        self._get_points()
        return self._points


class Marker(CombinedShape):
    def __init__(self, size):
        super().__init__()
        self._size = size
        self.add(Square(self._size))
        self.add(Square(self._size), position="TOPRIGHT_1")
        self.translate(-size, -size)

        self._points = {
            "ORIGIN": self.polygons[1][0],
            "BOTTOMLEFT": self.polygons[1][2],
            "TOPRIGHT": self.polygons[0][0],
            "END": self.polygons[1][0],
        }


class MarkerField(CombinedShape):
    def __init__(self, nx, ny, pitch):
        super().__init__()
        self._nx = nx
        self._ny = ny
        self._pitch = pitch

        for i in range(self._nx):
            for j in range(self._ny):
                marker = Square(5).translate(i * self._pitch, j * self._pitch)
                self.add(marker, add_points=False)
                self._points[f"MARKER_{i+1}_{j+1}"] = (i * self._pitch, j * self._pitch)

