import nanogds
import gdspy
import numpy as np
import string

PI = np.pi

if __name__ == "__main__":

    layer = 1
    layer2 = 2
    radius = 50000
    radius_offset = 500

    die_size = (8000, 4500)
    wafer_mapping = [
        range(4),
        range(10),
        range(16),
        range(18),
        range(20),
        range(20),
        range(20),
        range(20),
        range(18),
        range(16),
        range(10),
        range(4),
    ]

    ring = nanogds.Shape()
    ring.add(
        gdspy.Round(
            (0, 0), radius + radius_offset, inner_radius=radius - radius_offset
        ),
        layer=layer,
    )
    ring.add(
        gdspy.Round(
            (0, 0), radius + radius_offset, inner_radius=radius - radius_offset
        ),
        layer=layer2,
    )

    dicing = nanogds.Shape()
    angle = nanogds.Angle(500, 50, layer=layer).translate(25, 25)

    dicing.add(angle, position=(0, 0), angle=0)
    dicing.add(angle, position=(die_size[0], 0), angle=PI / 2)
    dicing.add(angle, position=(die_size[0], die_size[1]), angle=PI)
    dicing.add(angle, position=(0, die_size[1]), angle=-PI / 2)
    dicing.add(
        nanogds.Rectangle(die_size[0], die_size[1], layer=layer), operation="xor"
    )

    cross = nanogds.Cross(1000, 150, layer=layer2)
    cross.add(nanogds.Cross(1000, 50, layer=layer2), operation="not")
    dicing.add(cross, position=(0, 0))
    dicing.add(cross, position=(die_size[0], 0))
    dicing.add(cross, position=(die_size[0], die_size[1]))
    dicing.add(cross, position=(0, die_size[1]))
    dicing.add(
        nanogds.Rectangle(die_size[0], die_size[1], layer=layer2), operation="xor"
    )

    dicing_cell = gdspy.Cell(f"DICING_{die_size[0]}x{die_size[1]}um")
    dicing_cell.add(dicing.shapes)

    cell = gdspy.Cell("Template")

    ring_cell = gdspy.Cell("WAFER_RING_100mm")
    ring_cell.add(ring.shapes)
    cell.add(gdspy.CellReference(ring_cell))

    letters = string.ascii_uppercase

    center_i = len(wafer_mapping) / 2
    for i, column in enumerate(wafer_mapping):
        center_j = len(column) / 2
        for j in column:
            print(letters[i], j + 1)
            coords = ((i - center_i) * die_size[0], (center_j - j - 1) * die_size[1])
            die = gdspy.Cell(f"{letters[i]}{j+1}")
            # die.add(gdspy.CellReference(dicing_cell))
            cell.add(gdspy.CellReference(die, origin=coords))

    lib = gdspy.GdsLibrary()
    lib.add(cell)
    lib.write_gds("wafer_template_4x8mm.gds")
