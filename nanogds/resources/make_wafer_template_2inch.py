import nanogds
import gdspy
import numpy as np
import string

PI = np.pi

if __name__ == "__main__":

    layer = 1
    layer2 = 2
    radius = 25000
    radius_offset = 500

    die_size = (8000, 5000)
    wafer_mapping = [
        range(6),
        range(10),
        range(10),
        # range(10),
        range(10),
        range(10),
        range(10),
        range(6),
    ]

    ring = nanogds.Shape()
    ring.add(
        gdspy.Round((0, 0), radius + radius_offset, inner_radius=radius), layer=layer2,
    )

    cell = gdspy.Cell("Template")

    # ring_cell = gdspy.Cell("WAFER_RING_50mm")
    # ring_cell.add(ring.shapes)
    # cell.add(gdspy.CellReference(ring_cell))

    letters = string.ascii_uppercase

    center_i = len(wafer_mapping) / 2
    for i, column in enumerate(wafer_mapping):
        center_j = len(column) / 2
        for j in column:
            print(letters[i], j + 1)
            coords = (
                (center_j - j - 1) * die_size[1],
                (i - center_i + 1) * die_size[0],
            )
            die = gdspy.Cell(f"{letters[i]}{j+1}")
            cell.add(gdspy.CellReference(die, origin=coords, rotation=-90))

    lib = gdspy.GdsLibrary()
    lib.add(cell)
    lib.write_gds("wafer_template_2inch_5x8mm.gds")
