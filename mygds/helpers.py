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






