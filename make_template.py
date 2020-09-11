import mygds
import gdspy
import numpy as np
import string

PI = np.pi

if __name__ == "__main__":

    layer = 1
    layer2 = 2
    radius = 50000
    radius_offset = 500

    die_size = (9000, 5000)
    wafer_mapping = [
        range(8),
        range(12),
        range(16),
        range(18),
        range(18),
        range(18),
        range(18),
        range(16),
        range(12),
        range(8),
    ]

    print("TEST")

    ring = mygds.Shape()
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

    dicing = mygds.Shape()
    cross = mygds.Cross(1000, 50, layer=layer)
    dicing.add(cross, position=(0, 0))
    dicing.add(cross, position=(die_size[0], 0))
    dicing.add(cross, position=(die_size[0], die_size[1]))
    dicing.add(cross, position=(0, die_size[1]))

    cross = mygds.Cross(1000, 50, layer=layer2)
    dicing.add(cross, position=(0, 0))
    dicing.add(cross, position=(die_size[0], 0))
    dicing.add(cross, position=(die_size[0], die_size[1]))
    dicing.add(cross, position=(0, die_size[1]))

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
            die.add(gdspy.CellReference(dicing_cell))
            cell.add(gdspy.CellReference(die, origin=coords))

    lib = gdspy.GdsLibrary()
    lib.add(cell)
    lib.write_gds("template.gds")
