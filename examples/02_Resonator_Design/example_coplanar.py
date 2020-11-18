import nanogds
import numpy as np

PI = np.pi


if __name__ == "__main__":

    CPW_WIDTH = 10
    CPW_GAP = 6
    CPW_RADIUS = 100
    RESONATOR_MEANDER = 1000

    shape = nanogds.CoplanarShape()
    shape.add_to_ground(nanogds.Rectangle(8000, 2600).translate(500, 2300))
    shape.add_to_outer(nanogds.Rectangle(2500, 500).translate(3250, 4500))

    ### define coplanar shapes to be used

    # bondpad
    bondpad = nanogds.Bondpad(200, 300, 50, 100, CPW_WIDTH, CPW_GAP)
    bondpad.rotate(-PI / 2)

    # coplanar waveguide
    path1 = nanogds.CoplanarPath(CPW_WIDTH, CPW_GAP, CPW_RADIUS)
    path1.segment(800, "-y")
    path1.turn("l")
    path1.segment(500)

    path2 = nanogds.CoplanarPath(CPW_WIDTH, CPW_GAP, CPW_RADIUS)
    path2.segment(1800, "+x")
    path2.turn("l")
    path2.segment(RESONATOR_MEANDER / 2)
    path2.turn("rr")
    path2.segment(RESONATOR_MEANDER + 2 * CPW_RADIUS)
    path2.turn("ll")
    path2.segment(RESONATOR_MEANDER + 2 * CPW_RADIUS)
    path2.turn("rr")
    path2.segment(RESONATOR_MEANDER + 2 * CPW_RADIUS)
    path2.turn("ll")
    path2.segment(RESONATOR_MEANDER / 2)
    path2.turn("r")
    path2.segment(1800)

    path3 = nanogds.CoplanarPath(CPW_WIDTH, CPW_GAP, CPW_RADIUS)
    path3.segment(500, "+x")
    path3.turn("l")
    path3.segment(800)

    # capacitor
    capacitor1 = nanogds.FingerCapacitor(3, 20, CPW_WIDTH, CPW_GAP, total_length=100)
    capacitor2 = nanogds.FingerCapacitor(3, 20, CPW_WIDTH, CPW_GAP, total_length=100)

    ### combine coplanar shapes with main shape
    shape.combine(
        bondpad,
        position=[1500, 4300],
        connect_point=bondpad.points["END"],
        add_refs=True,
        counter=1,
    )
    shape.combine(
        path1, position=shape.points["BONDPAD #1 END"], add_refs=True, counter=1
    )
    shape.combine(
        capacitor1,
        position=shape.points["COPLANARPATH #1 END"],
        add_refs=True,
        counter=1,
    )
    shape.combine(
        path2,
        position=shape.points["FINGERCAPACITOR #1 SIDE 2"],
        add_refs=True,
        counter=2,
    )
    shape.combine(
        capacitor2,
        position=shape.points["COPLANARPATH #2 END"],
        add_refs=True,
        counter=2,
    )
    shape.combine(
        path3,
        position=shape.points["FINGERCAPACITOR #2 SIDE 2"],
        add_refs=True,
        counter=3,
    )
    shape.combine(
        bondpad,
        position=shape.points["COPLANARPATH #3 END"],
        connect_point=bondpad.points["END"],
        add_refs=True,
        counter=2,
    )

    print(f"RESONATOR LENGTH: {round(path2.length)} um\n\n")

    print(shape.points)

    ### add shape as cell to gds file
    lib = nanogds.GDS()
    lib.load_gds("Markerchip Variant A", "markerchip_variant_A.gds")
    lib.add("Resonator", shape.get_shape())
    lib.save("markerchip_with_resonator")
