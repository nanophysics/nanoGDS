import nanogds
import numpy as np

PI = np.pi


def get_cpw(center_width, gap, radius):
    path = nanogds.CoplanarPath(center_width, gap, radius)
    path.segment(300, "-y")
    path.turn("l")
    path.segment(200)
    path.turn("r")
    path.segment(500)
    path.turn("ll")
    path.segment(200)
    path.turn("rr")
    path.segment(200)
    path.turn("ll")
    path.segment(500)
    path.turn("r")
    path.segment(200)
    path.turn(-PI / 4)
    path.segment(200)
    path.turn(PI / 4)
    path.segment(200)
    path.turn(PI / 4)
    path.segment(200)
    path.turn(-PI / 4)
    path.segment(300)
    return path


if __name__ == "__main__":

    shape = nanogds.CoplanarShape()

    shape.add_to_ground(nanogds.Rectangle(4000, 2000).translate(-2000, -1000))
    shape.add_to_outer(nanogds.Rectangle(600, 200).translate(-300, 900))

    ### define coplanar shapes to be used

    # bondpad
    bondpad = nanogds.Bondpad(200, 300, 50, 100, 10, 20)
    bondpad.rotate(-PI / 2)

    # coplanar waveguide
    path = get_cpw(10, 20, 80)

    ### combine coplanar shapes with main shape
    shape.combine(bondpad, position=[-1000, 800], add_refs=True)
    shape.combine(path, position=shape.points["BONDPAD END"], add_refs=True)
    shape.combine(
        bondpad.rotate(-PI / 2),
        position=shape.points["COPLANARPATH END"],
        connect_point=bondpad.points["END"],
        add_refs=True,
    )

    print(shape.points)

    ### add shape as cell to gds file
    lib = nanogds.GDS()
    lib.add_cell("TEST", shape.get_shape())
    lib.save("testchip")
