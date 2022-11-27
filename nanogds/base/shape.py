import gdspy
import numpy as np
from copy import deepcopy

from .reference import Reference


class Shape:
    def __init__(self):
        self._reference = Reference()
        self._shapes = {}
        self.add_reference("ORIGIN", (0, 0))
        self._draw()

    def translate(self, dx, dy):
        for shape in self._shapes.values():
            shape.translate(dx, dy)
        self._reference.translate(dx, dy)
        return self

    def rotate(self, radians, center=(0, 0)):
        for shape in self._shapes.values():
            shape.rotate(radians, center)
        self._reference.rotate(radians, center)
        return self

    def scale(self, scalex, scaley=None, center=(0, 0)):
        for shape in self._shapes.values():
            shape.scale(scalex, scaley, center)
        self._reference.scale(scalex, scaley, center)
        return self

    def mirror(self, p1, p2=(0, 0)):
        for shape in self._shapes.values():
            shape.mirror(p1, p2)
        self._reference.mirror(p1, p2)
        return self

    def fillet(self, radius):
        for shape in self._shapes.values():
            shape.fillet(radius)
        return self

    def offset(self, distance):
        for key, shape in self._shapes.items():
            self._shapes[key] = gdspy.offset(shape, distance)
        #self._reference.offset(distance)
        return self

    def change_layer(self, layer, original_layer=0):
        if isinstance(layer, int):
            for shape in self._shapes.values():
                shape.layers = [layer] * len(shape.layers)
            self._shapes = {layer: self._shapes[original_layer]}
        else:
            raise Error("Layer must be an integer number.")

    def add(
        self,
        element,
        position=None,
        angle=None,
        layer=0,
        add_refs=False,
        counter=None,
        operation="or",
    ):
        element = deepcopy(element)
        if angle is not None:
            element.rotate(angle)
        if position is not None:
            element.translate(position[0], position[1])

        if isinstance(element, Shape):
            for l in element.layers:
                self._add_polygonset(element._shapes[l], layer=l, operation=operation)
            if add_refs:
                self._merge_references(element, counter)
        elif isinstance(element, gdspy.polygon.PolygonSet):
            self._add_polygonset(element, layer, operation=operation)
        elif isinstance(element, gdspy.FlexPath):
            self._add_polygonset(element.get_polygons(), layer, operation=operation)
        else:
            raise Exception(
                f"Element to add needs to be either a `Shape` or `gdspy.PolygonSet`. This is a {element}"
            )

    def _add_polygonset(self, element, layer=0, operation="or"):
        operation = operation.lower()
        if operation not in ["or", "and", "not", "xor"]:
            raise Exception(f"Unknown operation '{operation}'")
        if layer not in self._shapes.keys():
            self._shapes[layer] = gdspy.PolygonSet([], layer=layer)  # new layer
        self._shapes[layer] = gdspy.boolean(
            self._shapes[layer], element, operation, layer=layer
        )

    def add_reference(self, name, point):
        self._reference.add(name, point)

    def _merge_references(self, element, counter):
        for name, point in element.points.items():
            if name == "ORIGIN":
                continue
            new_name = type(element).__name__.upper()
            if counter is not None:
                new_name += f" #{counter}"
            new_name += f" {name}"
            self.add_reference(new_name, point)

    def _draw(self):
        pass

    @property
    def shapes(self):
        return list(self._shapes.values())

    @property
    def layers(self):
        return list(self._shapes.keys())

    @property
    def polygons(self):
        return [shape.polygons for shape in self._shapes.values()]

    @property
    def points(self):
        return self._reference.points
