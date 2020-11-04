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
    path._draw()

    ########################################

    # coplanar_shape = nanogds.CoplanarShape()
    # coplanar_shape.add_to_ground(nanogds.Rectangle(4000, 2000).translate(-2000, -1000))

    bondpad = nanogds.Bondpad(200, 300, 50, 200, 20, 10)
    # # bondpad.rotate(-PI / 2)
    # coplanar_shape.combine(bondpad, point=[1000, 0], add_refs=True, counter=1)

    # # print(coplanar_shape.points)

    # # coplanar_shape.combine(path, point=[0, 100], add_refs=True, counter=1)

    # # shape.add(path, position=[1000, 0])
    test = nanogds.Shape()
    test.add(nanogds.Rectangle(300, 300), position=(-150, -150))
    test.translate(0, 100)

    shape.add(test, position=[0, 0])

    lib = nanogds.GDS()
    lib.add_cell("TEST", shape)
    lib.save("testchip")
