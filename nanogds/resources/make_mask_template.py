import nanogds
import gdspy
import numpy as np
import string

PI = np.pi


class Angle(nanogds.Shape):
    def __init__(self, w, l):
        self._w, self._l = w, l
        super().__init__()

    def _draw(self):
        self.add(nanogds.Rectangle(self._w, self._l).translate(-self._w, -self._w))
        self.add(nanogds.Rectangle(self._l, self._w).translate(-self._w, -self._w))


if __name__ == "__main__":

    layer = 0
    die_size = (9000, 5000)
    gap1 = 0
    gap2_x = 1000
    gap2_y = 500

    n_x = 5
    n_y = 9

    n_copies = 1

    width_mask = n_x * die_size[0] + (n_x + 1) * gap2_x
    width_frame = 2000

    w = width_mask + width_frame
    frame = nanogds.Rectangle(w, w, layer=layer).translate(-w / 2, -w / 2)
    frame.add(
        nanogds.Rectangle(width_mask, width_mask, layer=layer).translate(
            -width_mask / 2, -width_mask / 2
        ),
        operation="not",
    )

    # main cell
    cell = gdspy.Cell("Template")

    # add frame to cell as referece
    frame_cell = gdspy.Cell("MASK_FRAME")
    frame_cell.add(frame.shapes)
    cell.add(gdspy.CellReference(frame_cell))

    # dicing cell
    die_frame = gdspy.Cell("DIE_FRAME")
    shape = nanogds.Shape()
    angle = Angle(25, 250)
    shape.add(angle, position=[0, 0], angle=0)
    shape.add(angle, position=[die_size[0], 0], angle=PI / 2)
    shape.add(angle, position=[0, die_size[1]], angle=-PI / 2)
    shape.add(angle, position=die_size, angle=PI)
    die_frame.add(shape.shapes)

    letters = string.ascii_uppercase
    center_i = n_x / 2
    center_j = n_y / 2

    for i in range(n_x):
        for j in range(n_y):
            print(letters[i], j + 1)
            coords = (
                (i - center_i) * (die_size[0] + gap2_x) + gap2_x / 2,
                (center_j - j) * (n_copies * die_size[1] + 2 * gap1 + gap2_y)
                - die_size[1]
                - gap2_y / 2,
            )

            die = gdspy.Cell(f"{letters[i]}{j+1}")
            die.add(gdspy.CellReference(die_frame))
            cell.add(
                gdspy.Text(
                    f"{letters[i]}{j+1}",
                    size=400,
                    position=[coords[0] - 750, coords[1] + die_size[1] - 400],
                )
            )
            for n in range(n_copies):
                cell.add(
                    gdspy.CellReference(
                        die, origin=[coords[0], coords[1] - n * (die_size[1] + gap1)]
                    )
                )

    lib = gdspy.GdsLibrary()
    lib.add(cell)
    lib.write_gds("mask_template_5x9.gds")
