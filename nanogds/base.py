import gdspy
import numpy as np
from copy import deepcopy


class GDS:
    def __init__(self):
        self._lib = gdspy.GdsLibrary()
        self._main_cell = self._lib.new_cell("MAIN")

    def add_cell(self, name, shapes, origin=(0, 0)):
        cell = gdspy.Cell(name)
        if isinstance(shapes, list):
            for s in shapes:
                cell = self._add_element_to_cell(cell, s, origin)
        else:
            cell = self._add_element_to_cell(cell, shapes, origin)
        self._main_cell.add(cell)

    def _add_element_to_cell(self, cell, element, origin):
        element = deepcopy(element)
        element.translate(origin[0], origin[1])
        if isinstance(element, Shape):
            cell.add(element.shapes)
        else:
            cell.add(element)
        return cell

    def save(self, name):
        self._lib.write_gds(f"{name}.gds")


class FourInchWafer:
    def __init__(
        self,
        path_to_template="C:\\Users\\maxru\\PhD\\Code\\mygds\\mygds\\resources\\template.gds",
    ):
        self._lib = gdspy.GdsLibrary(infile=path_to_template)

    def add_reference(self, name, shape, add_to):
        newcell = self._lib.new_cell(name, overwrite_duplicate=True)
        newcell.add(shape)
        newcell_ref = gdspy.CellReference(newcell)
        counter = 0
        for ref in self._lib.cells["Template"].references:
            if ref.ref_cell.name in add_to:
                ref.ref_cell.add(newcell_ref)
                counter += 1
                print(
                    f"{counter}: Added reference to cell '{name}' to '{ref.ref_cell.name}'"
                )

    def add_reference_by_columns(self, name, shape, columns):
        newcell = self._lib.new_cell(name, overwrite_duplicate=True)
        newcell.add(shape)
        newcell_ref = gdspy.CellReference(newcell)
        counter = 0
        for ref in self._lib.cells["Template"].references:
            for column in columns:
                if ref.ref_cell.name.startswith(column):
                    ref.ref_cell.add(newcell_ref)
                    counter += 1
                    print(
                        f"{counter}: Added reference to cell '{name}' to '{ref.ref_cell.name}'"
                    )

    def add_reference_to_all(self, name, shape):
        newcell = self._lib.new_cell(name, overwrite_duplicate=True)
        newcell.add(shape)
        newcell_ref = gdspy.CellReference(newcell)
        counter = 0
        for ref in self._lib.cells["Template"].references:
            if ref.ref_cell.name.startswith("WAFER_RING"):
                continue
            ref.ref_cell.add(newcell_ref)
            counter += 1
            print(
                f"{counter}: Added reference to cell '{name}' to '{ref.ref_cell.name}'"
            )

    def write(self, name):
        self._lib.write_gds(f"{name}.gds")


class Shape:
    def __init__(self):
        self._n_elements = 0
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

    def add(
        self, element, position=None, angle=None, layer=0, add_refs=False, counter=None,
    ):
        element = deepcopy(element)
        if angle is not None:
            element.rotate(angle)
        if position is not None:
            element.translate(position[0], position[1])

        if isinstance(element, Shape):
            for l in element.layers:
                self._add_polygonset(element._shapes[l], layer=l)
            if add_refs:
                self._merge_references(element, counter)
        elif isinstance(element, gdspy.polygon.PolygonSet):
            self._add_polygonset(element, layer)
        elif isinstance(element, gdspy.FlexPath):
            self._add_polygonset(element.get_polygons(), layer)
        else:
            raise Exception(
                "Element to add needs to be either a `Shape` or `gdspy.PolygonSet`"
            )

    def _add_polygonset(self, element, layer=0):
        if layer not in self._shapes.keys():
            self._shapes[layer] = gdspy.PolygonSet([], layer=layer)  # new layer
        self._shapes[layer] = gdspy.boolean(
            self._shapes[layer], element, "or", layer=layer
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

