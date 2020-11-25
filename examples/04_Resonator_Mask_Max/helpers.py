import nanogds
import gdspy
import numpy as np

PI = np.pi


class Angle(nanogds.Shape):
    def __init__(self, w, l):
        self._w, self._l = w, l
        super().__init__()

    def _draw(self):
        self.add(nanogds.Rectangle(self._w, self._l).translate(-self._w, -self._w))
        self.add(nanogds.Rectangle(self._l, self._w).translate(-self._w, -self._w))


class AngleMarker(nanogds.Shape):
    def __init__(self, w, l, offset):
        self._w, self._l, self._offset = w, l, offset
        super().__init__()

    def _draw(self):
        angle = Angle(self._w, self._l).translate(self._offset, self._offset)
        self.add(angle)
        self.add(angle.rotate(PI))


class FingerGateTap(nanogds.CoplanarShape):
    def __init__(self, w1, w2, w3, l):
        self._w1, self._w2, self._w3, self._l = w1, w2, w3, l
        super().__init__()

    def _draw(self):
        self.add_to_outer(
            gdspy.Polygon(
                [
                    [-self._w1 / 2, 0],
                    [self._w1 / 2, 0],
                    [self._w2 / 2, -self._l],
                    [-self._w2 / 2, -self._l],
                ]
            )
        )
        self.add_to_center(
            nanogds.Rectangle(self._w3, -self._l).translate(-self._w3 / 2, 0)
        )
        self.add_to_center(nanogds.Rectangle(20, 20).translate(-10, -self._l - 10))


def get_resonator_shape(
    finger_length=20,
    finger_gap=3,
    cpw_width=10,
    cpw_gap=6,
    cpw_radius=100,
    resonator_meander=150,
    extend_ground=True,
    add_tap1=True,
    add_tap2=True,
    add_center_tap=True,
    add_ground_connection=False,
    add_center_ground_connection=False,
):
    CPW_WIDTH = cpw_width
    CPW_GAP = cpw_gap
    CPW_RADIUS = cpw_radius
    RESONATOR_MEANDER = resonator_meander

    shape = nanogds.CoplanarShape()
    shape.add_to_ground(nanogds.Rectangle(7500, 2210).translate(750, 2240))
    if extend_ground:
        # shape.add_to_outer(nanogds.Rectangle(2500, 500).translate(3250, 4500))
        shape.add_to_outer(nanogds.Rectangle(60, 60).translate(4170, 2170))
        shape.add_to_outer(nanogds.Rectangle(60, 60).translate(4770, 2170))
        shape.add_to_outer(nanogds.Rectangle(60, 60).translate(4170, 1610))
        shape.add_to_outer(nanogds.Rectangle(60, 60).translate(4770, 1610))
        if add_center_ground_connection:
            shape.add_to_ground(
                gdspy.Polygon([[3750, 2250], [3750, 1460], [5250, 1460], [5250, 2250],])
            )
        else:
            # outline of center bondpad and lead
            shape.add_to_ground(
                gdspy.Polygon(
                    [
                        [3750, 2250],
                        [3750, 1400],
                        [4150, 700],
                        [4150, 50],
                        [4850, 50],
                        [4850, 700],
                        [5250, 1400],
                        [5250, 2250],
                    ]
                )
            )
            shape.add_to_outer(
                gdspy.Polygon(
                    [
                        [4350, 150],
                        [4650, 150],
                        [4650, 550],
                        [4550, 700],
                        [4550, 1750],
                        [4450, 1750],
                        [4450, 700],
                        [4350, 550],
                    ]
                )
            )
    if add_center_tap:
        shape.add_to_outer(
            nanogds.Rectangle(400, 640).translate(4500, 1960).translate(-200, -400)
        )
        shape.add_to_outer(
            nanogds.Rectangle(20, 100).translate(4500, 2280).translate(-10, -100)
        )
        shape.add_to_center(
            nanogds.Rectangle(5, 100).translate(4500, 2280).translate(-2.5, -100)
        )

    if add_ground_connection:
        shape.add_to_ground(get_HF_mask(1030, 790, 4000, 5000, 2250))
        shape.add_to_outer(nanogds.Rectangle(-680, -680).translate(3750, 2240))
        shape.add_to_outer(nanogds.Rectangle(680, -680).translate(5250, 2240))

    shape.add_to_ground(AngleMarker(5, 25, 10).translate(200, 4800))
    shape.add_to_ground(AngleMarker(5, 25, 10).rotate(-PI).translate(8800, 200))
    shape.add_to_ground(AngleMarker(5, 25, 10).rotate(-PI / 2).translate(8800, 4800))
    shape.add_to_ground(AngleMarker(5, 25, 10).rotate(PI / 2).translate(200, 200))

    ### define coplanar shapes to be used

    # bondpad
    bondpad = nanogds.Bondpad(160, 200, 100, 200, CPW_WIDTH, CPW_GAP)
    bondpad.rotate(-PI / 2)

    # coplanar waveguide
    path1 = nanogds.CoplanarPath(CPW_WIDTH, CPW_GAP, CPW_RADIUS)
    path1.segment(270, "-y")
    path1.turn("l")
    path1.segment(1650)
    path1.turn("r")
    path1.segment(800)

    path2 = nanogds.CoplanarPath(CPW_WIDTH, CPW_GAP, CPW_RADIUS)
    path2.segment(0, "-y")
    path2.turn("l")
    path2.segment(100)
    path2.turn("l")
    path2.segment(1000 + RESONATOR_MEANDER)
    path2.turn("rr")
    path2.segment(2 * RESONATOR_MEANDER)
    path2.turn("ll")
    path2.segment(2 * RESONATOR_MEANDER)
    path2.turn("rr")
    path2.segment(1000 + RESONATOR_MEANDER)
    path2.turn("l")
    path2.segment(300)
    path2.turn("l")
    path2.segment(1000 + RESONATOR_MEANDER)
    path2.turn("rr")
    path2.segment(2 * RESONATOR_MEANDER)
    path2.turn("ll")
    path2.segment(2 * RESONATOR_MEANDER)
    path2.turn("rr")
    path2.segment(1000 + RESONATOR_MEANDER)
    path2.turn("l")
    path2.segment(100)
    path2.turn("l")

    # capacitor
    capacitor1 = nanogds.FingerCapacitor(
        finger_gap, finger_length, CPW_WIDTH, CPW_GAP, total_length=100
    )
    capacitor2 = nanogds.FingerCapacitor(
        finger_gap, finger_length, CPW_WIDTH, CPW_GAP, total_length=100
    )

    ### combine coplanar shapes with main shape
    shape.combine(
        bondpad,
        position=[1500, 3750],
        connect_point=bondpad.points["END"],
        add_refs=True,
        counter=1,
    )
    shape.combine(
        path1, position=shape.points["BONDPAD #1 END"], add_refs=True, counter=1
    )
    shape.combine(
        capacitor1.rotate(-PI / 2),
        position=shape.points["COPLANARPATH #1 END"],
        add_refs=True,
        counter=1,
    )
    if add_tap1:
        shape.combine(
            FingerGateTap(10, 100, 5, 100),
            position=np.array(shape.points["FINGERCAPACITOR #1 SIDE 2"])
            + np.array([150, -100]),
            add_refs=True,
            counter=1,
        )
    shape.combine(
        path2,
        position=shape.points["FINGERCAPACITOR #1 SIDE 2"],
        add_refs=True,
        counter=2,
    )
    if add_tap2:
        shape.combine(
            FingerGateTap(10, 100, 5, 100),
            position=np.array(shape.points["COPLANARPATH #2 END"])
            + np.array([-150, -100]),
            add_refs=True,
            counter=2,
        )
    shape.combine(
        capacitor2.rotate(PI / 2),
        position=shape.points["COPLANARPATH #2 END"],
        add_refs=True,
        counter=2,
    )
    shape.combine(
        path1.mirror([0, 1]),
        position=shape.points["FINGERCAPACITOR #2 SIDE 2"],
        connect_point=path1.points["END"],
        add_refs=True,
        counter=3,
    )
    shape.combine(
        bondpad,
        position=shape.points["COPLANARPATH #3 START"],
        connect_point=bondpad.points["END"],
        add_refs=True,
        counter=2,
    )

    print(f"RESONATOR LENGTH: {round(path2.length)} um\n\n")

    return_shape = nanogds.Shape()
    return_shape.add(shape.get_shape())
    return return_shape


def get_EBR_mask(width, height, dx, dy):
    shape = nanogds.Shape()
    shape.add(nanogds.Rectangle(width, height), position=[dx, dy])
    return shape


def get_HF_mask(width, height, x1, x2, y, center=False):
    shape = nanogds.Shape()
    shape.add(
        gdspy.Polygon(
            [[x1, y], [x1 - width, y], [x1 - width, y - height], [x1, y - height],]
        )
    )
    shape.add(
        gdspy.Polygon(
            [[x2, y], [x2 + width, y], [x2 + width, y - height], [x2, y - height],]
        )
    )
    shape.add(
        nanogds.Rectangle(100, 120).translate(-50, -120),
        position=[x1 - 500, y],
        operation="not",
    )
    shape.add(
        nanogds.Rectangle(100, 120).translate(-50, -120),
        position=[x2 + 500, y],
        operation="not",
    )
    if center:
        shape.add(
            nanogds.Rectangle(1000, 450).translate(-500, 0),
            position=[4500, y - height],
        )
    return shape

