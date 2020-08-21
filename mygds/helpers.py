from abc import ABC, abstractmethod

import gdspy
import numpy as np


class Chip:
    def __init__(self):
        self.lib = gdspy.GdsLibrary()
        gdspy.current_library = self.lib
        self._shapes = []

    def add(self, shape):
        self._shapes.append(shape)

    @property
    def shapes(self):
        return self._shapes

    def create_cell(self, name="layer0"):
        cell = gdspy.Cell(name)
        for shape in self.shapes:
            cell.add(shape.shape)
        self.lib.add(cell, overwrite_duplicate=True)

    def write_gds(self, name):
        self.lib.write_gds(f"{name}.gds")


class Reference:
    def __init__(self):
        self._points = {}

    def add(self, name, point):
        self._points[name] = np.array(point)

    def translate(self, dx, dy):
        shape = self._get_shape()
        shape.translate(dx, dy)
        self._get_points_from_shape(shape)

    def rotate(self, radians, center=(0, 0)):
        shape = self._get_shape()
        shape.rotate(radians, center)
        self._get_points_from_shape(shape)

    def scale(self, scalex, scaley=None, center=(0, 0)):
        shape = self._get_shape()
        shape.scale(scalex, scaley, center)
        self._get_points_from_shape(shape)

    def mirror(self, p1, p2=(0, 0)):
        shape = self._get_shape()
        shape.mirror(p1, p2)
        self._get_points_from_shape(shape)

    def _get_shape(self):
        points = [p for p in self._points.values()]
        return gdspy.Polygon(points)

    def _get_points_from_shape(self, shape):
        point_lst = list(shape.polygons[0])
        for i, name in enumerate(self._points.keys()):
            self._points[name] = point_lst[i]

    @property
    def points(self):
        return self._points
