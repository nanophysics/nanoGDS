import gdspy
import numpy as np
from copy import deepcopy
import os

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

from .. import resources
from .shape import Shape


class GDS:
    def __init__(self):
        self._lib = gdspy.GdsLibrary()
        self._top_cell = self._lib.new_cell("TOP")

    def add(self, name, shapes, origin=(0, 0)):
        cell = self._lib.new_cell(name)
        if isinstance(shapes, list):
            for s in shapes:
                self._add_to_cell(cell, s, origin)
        else:
            self._add_to_cell(cell, shapes, origin)
        cell_ref = gdspy.CellReference(cell)
        self._top_cell.add(cell_ref)

    def _add_to_cell(self, cell, element, origin):
        element = deepcopy(element)
        if isinstance(element, Shape):
            cell.add(element.shapes)
        else:
            cell.add(element)
        return cell

    def load_gds(self, cell_name, path="eth.gds"):
        self._lib.read_gds(path)
        cell_ref = gdspy.CellReference(self._lib.cells[cell_name])
        self._top_cell.add(cell_ref)

    def translate_cell(self, name, dx, dy):
        for p in self._lib.cells[name].polygons:
            p.translate(dx, dy)

    def save(self, name):
        self._lib.write_gds(f"{name}.gds")


class MaskTemplate:
    def __init__(
        self, template="wafer_template",
    ):
        path_to_template = os.path.join(resources.__path__[0], template + ".gds")
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
