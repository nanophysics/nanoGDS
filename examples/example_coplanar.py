import nanogds
import numpy as np

PI = np.pi

if __name__ == "__main__":

    shape = nanogds.Shape()

    # path = nanogds.CoplanarPath(10, 20, 80)
    # path.segment(500)
    # path.turn("l")
    # path.segment(500)
    # path.turn("r")
    # path.segment(500)
    # path.turn(-1 / 4 * PI)
    # path.segment(500)
    # path.turn(-1 / 4 * PI)
    # path.segment(500)
    # path.turn(-1 / 4 * PI)
    # path.segment(500)
    # path.turn(-1 / 4 * PI)
    # path.segment(1000)
    # path.turn("r")
    # path.segment(100)
    # path.turn("ll")
    # path.turn("r")
    # path.segment(1000)

    c = nanogds.RectangleCapacitor(100, 200, 20)
    s = c.get_shape()
    s.translate(1000, 500)
    print(s.points)

    bondpad = nanogds.Bondpad(200, 300, 20, 100, 20, 5)
    b = bondpad.get_shape()
    b.rotate(-PI / 2)
    b.translate(-1000, 0)

    print(b.points)

    shape.add(b, add_refs=True, counter=1)
    shape.add(s, position=shape.points["BONDPAD #1 END"], add_refs=True, counter=1)
    print(shape.points)

    lib = nanogds.GDS()
    lib.add_cell("TEST", shape)
    lib.save("testchip")
