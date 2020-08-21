import gdspy
import numpy as np

from copy import deepcopy


class Shape:
    def __init__(self):
        self._n_elements = 0
        self._reference = Reference()
        self._shape = gdspy.PolygonSet([])
        self.add_reference("ORIGIN", (0, 0))
        self._draw()

    def translate(self, dx, dy):
        self._shape.translate(dx, dy)
        self._reference.translate(dx, dy)
        return self

    def rotate(self, radians, center=(0, 0)):
        self._shape.rotate(radians, center)
        self._reference.rotate(radians, center)
        return self

    def scale(self, scalex, scaley=None, center=(0, 0)):
        self._shape.scale(scalex, scaley, center)
        self._reference.scale(scalex, scaley, center)
        return self

    def mirror(self, p1, p2=(0, 0)):
        self._shape.mirror(p1, p2)
        self._reference.mirror(p1, p2)
        return self

    def add(self, element, position=None, add_refs=False, counter=None):
        element = deepcopy(element)
        if position is not None:
            element.translate(position[0], position[1])
        if isinstance(element, Shape):
            self._shape = gdspy.boolean(self._shape, element.shape, "or")
            if add_refs:
                self._merge_references(element, counter)
        elif isinstance(element, gdspy.polygon.PolygonSet):
            self._shape = gdspy.boolean(self._shape, element, "or")
        else:
            raise Exception(
                "Element to add needs to be either a `Shape` or `gdspy.PolygonSet`"
            )

    def add_reference(self, name, point):
        self._reference.add(name, point)

    def _merge_references(self, element, counter):
        for name, point in element.points.items():
            if name == "ORIGIN":
                continue

            new_name = f"{type(element).__name__.upper()}"
            if counter is not None:
                new_name += f" #{counter}"
            new_name += f" {name}"
            self.add_reference(new_name, point)

    def _draw(self):
        pass

    @property
    def shape(self):
        return self._shape

    @property
    def polygons(self):
        return self.shape.polygons

    @property
    def points(self):
        return self._reference.points


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
