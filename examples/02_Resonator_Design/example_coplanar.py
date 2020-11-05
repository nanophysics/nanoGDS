import nanogds
import numpy as np

PI = np.pi


def get_cpw(center_width, gap, radius):
    path = nanogds.CoplanarPath(center_width, gap, radius)
    path.segment(500, "-y")
    path.turn("l")
    path.segment(1000)
    path.turn("r")
    path.segment(500)
    path.turn("ll")
    path.segment(500)
    path.turn("rr")
    path.segment(500)
    path.turn("ll")
    path.segment(500)
    path.turn("r")
    path.segment(500)
    path.turn(-PI / 4)
    path.segment(500)
    path.turn(PI / 4)
    path.segment(500)
    path.turn(PI / 4)
    path.segment(500)
    path.turn(-PI / 4)
    path.segment(1000)
    return path


if __name__ == "__main__":

    shape = nanogds.CoplanarShape()

    shape.add_to_ground(nanogds.Rectangle(8000, 2600).translate(500, 2300))
    shape.add_to_outer(nanogds.Rectangle(2500, 500).translate(3250, 4500))

    ### define coplanar shapes to be used

    # bondpad
    bondpad = nanogds.Bondpad(200, 300, 50, 100, 10, 20)
    bondpad.rotate(-PI / 2)

    # coplanar waveguide
    path = get_cpw(10, 20, 80)

    ### combine coplanar shapes with main shape
    shape.combine(
        bondpad,
        position=[1500, 4200],
        connect_point=bondpad.points["END"],
        add_refs=True,
    )
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
    lib.load_gds("Markerchip Variant A", "markerchip_variant_A.gds")
    lib.add("Resonator", shape.get_shape())
    lib.save("markerchip_with_resonator")
