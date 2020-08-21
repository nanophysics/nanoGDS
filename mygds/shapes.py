from .base import Shape, Reference

import gdspy


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


class Marker(Shape):
    def __init__(self, size):
        self._size = size
        super().__init__()

    def _draw(self):
        self.add(Square(self._size), position=(-self._size, -self._size))
        self.add(Square(self._size))
        self.add_reference("CENTER", (0, 0))


class MarkerField(Shape):
    def __init__(self, size, nx, ny, pitch):
        self._size = size
        self._nx = nx
        self._ny = ny
        self._pitch = pitch
        super().__init__()

    def _draw(self):
        for i in range(self._nx):
            for j in range(self._ny):
                position = (i * self._pitch, j * self._pitch)
                self.add(Marker(self._size), position=position)
                self.add_reference(f"MARKER_{i+1}_{j+1}", position)
