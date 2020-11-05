import gdspy
import numpy as np
from copy import deepcopy

from .shape import Shape


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
