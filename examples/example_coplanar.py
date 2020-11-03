import nanogds
import numpy as np

PI = np.pi

if __name__ == "__main__":

    shape = nanogds.Shape()

    path = nanogds.CoplanarPath(10, 20, 80)
    path.segment(500)
    path.turn("l")
    path.segment(500)
    path.turn("r")
    path.segment(500)
    path.turn(-1 / 4 * PI)
    path.segment(500)
    path.turn(-1 / 4 * PI)
    path.segment(500)
    path.turn(-1 / 4 * PI)
    path.segment(500)
    path.turn(-1 / 4 * PI)
    path.segment(1000)
    path.turn("r")
    path.segment(100)
    path.turn("ll")
    path.turn("r")
    path.segment(1000)
    print(path.points, path.length)

    coplanar_shape = nanogds.CoplanarShape()
    coplanar_shape.add_to_ground(nanogds.Rectangle(4000, 2000).translate(-2000, -1000))

    coplanar_shape.combine(path)
    coplanar_shape.combine(nanogds.RectangleCapacitor(100, 200, 10))

    shape.add(coplanar_shape)

    lib = nanogds.GDS()
    lib.add_cell("TEST", shape)
    lib.save("testchip")
