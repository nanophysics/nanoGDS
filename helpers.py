import gdspy
import numpy as np
import mygds


def get_marker_field(
    size=500,
    marker_size=5,
    pitch=100,
    n_connections=6,
    connection_sides=["left", "bottom"],
    layer=0,
):
    f = mygds.MarkerField(marker_size, 2, 2, size, layer=layer)
    f.add_corners()
    n = int(size / pitch)
    f.add(
        mygds.MarkerField(marker_size, n - 1, n - 1, pitch, label=True, layer=layer),
        position=(pitch, pitch),
    )
    f.add(mygds.MarkerField(marker_size, n + 1, n + 1, pitch, layer=layer))
    for side in connection_sides:
        f.add_connection_points(n_connections, side)
    return f


class MarkersInCorners(mygds.Shape):
    def __init__(
        self,
        chip_size=(8000, 4000),
        marker_size=50,
        marker_offset=(100, 100),
        flip=False,
        layer=0,
    ):
        self._chip_size = np.array(chip_size)
        self._marker_size = marker_size
        self._marker_offset = np.array(marker_offset)
        self._flip = flip
        self._layer = layer
        super().__init__()

    def _draw(self):
        marker = mygds.Marker(self._marker_size, layer=self._layer)
        positions = [
            self._marker_offset,
            (self._chip_size[0] - self._marker_offset[0], self._marker_offset[1],),
            (
                self._chip_size[0] - self._marker_offset[0],
                self._chip_size[1] - self._marker_offset[1],
            ),
            (self._marker_offset[0], self._chip_size[1] - self._marker_offset[1]),
        ]
        if self._flip:
            angles = [(i + 1) * np.pi / 2 for i in range(4)]
        else:
            angles = [i * np.pi / 2 for i in range(4)]
        for i, (pos, angle) in enumerate(zip(positions, angles)):
            self.add(
                marker, position=pos, angle=angle, add_refs=True, counter=i + 1,
            )


def write_numbers(
    bondpad_coords, size=40, offset1=100, offset2=15, chip_width=8000, layer=0
):
    shape = mygds.Shape()
    for i, pos in enumerate(bondpad_coords):
        text = gdspy.Text(f"{i+1}", size)
        if i in range(4):
            pos = (pos[0] - offset1, pos[1] + offset2)
            shape.add(text, angle=-np.pi / 2, position=pos, layer=layer)
            mirror_pos = (chip_width - pos[0] + offset2, pos[1] - offset2)
            shape.add(text, angle=np.pi / 2, position=mirror_pos, layer=layer)
        else:
            pos = (pos[0] - offset2, pos[1] - offset1)
            shape.add(text, position=pos, layer=layer)
            mirror_pos = (chip_width - pos[0] - 40, pos[1])
            shape.add(text, position=mirror_pos, layer=layer)
    return shape


def get_bondpads_coordinates(
    n_left=4,
    n_bottom=8,
    p1_left=1500,
    p2_left=500,
    p1_bottom=1000,
    p2_bottom=3500,
    offset=300,
    distance_to_edge=200,
):
    y_coords_left = np.linspace(p1_left, p2_left, n_left)
    x_coords_bottom = np.linspace(p1_bottom, p2_bottom, n_bottom)
    bondpads_1 = [(distance_to_edge, y) for y in y_coords_left] + [
        (x, distance_to_edge) for x in x_coords_bottom
    ]
    bondpads_2 = [(distance_to_edge + offset, y) for y in y_coords_left] + [
        (x, distance_to_edge + offset) for x in x_coords_bottom
    ]
    return bondpads_1, bondpads_2


def get_intermediate_points(
    n_left=4,
    n_bottom=8,
    p1_left=1600,
    p2_left=1000,
    p1_bottom=1500,
    p2_bottom=3500,
    offset_left=800,
    offset_bottom=1000,
    slope_left=100,
    slope_bottom=40,
):
    y_coords_left = np.linspace(p1_left, p2_left, n_left)
    x_coords_bottom = np.linspace(p1_bottom, p2_bottom, n_bottom)
    points_left = [
        (offset_left + slope_left * i, y) for i, y in enumerate(y_coords_left)
    ]
    points_bottom = [
        (x, offset_bottom - i * slope_bottom) for i, x in enumerate(x_coords_bottom)
    ]
    return points_left + points_bottom


def get_final_points(
    shape_points,
    n_left=6,
    n_bottom=6,
    offset1_left=-50,
    offset1_bottom=-50,
    slope_left=50,
    slope_bottom=25,
    offset2_left=20,
    offset2_bottom=20,
):
    final1 = [
        shape_points[f"MARKERFIELD #1 LEFT #{i+1}"]
        + np.array([offset1_left - slope_left * (n_left - 1 - i), 0])
        for i in range(n_left)
    ] + [
        shape_points[f"MARKERFIELD #1 BOTTOM #{i+1}"]
        + np.array([0, offset1_bottom - slope_bottom * i])
        for i in range(n_bottom)
    ]

    final2 = [
        shape_points[f"MARKERFIELD #1 LEFT #{i+1}"] + np.array([offset2_left, 0])
        for i in range(n_left)
    ] + [
        shape_points[f"MARKERFIELD #1 BOTTOM #{i+1}"] + np.array([0, offset2_bottom])
        for i in range(n_bottom)
    ]

    return final1, final2


def get_logo(path="eth.gds", layer=0):
    # local cdes folder
    logo_lib = gdspy.GdsLibrary(infile=path)
    gdspy.current_library = logo_lib
    # import cell
    cell = logo_lib.extract("TOP")
    mit = cell.get_polygons()
    return gdspy.fast_boolean(mit, None, "or", max_points=0, layer=layer)

