import nanogds
import gdspy
import numpy as np
import helpers
from copy import deepcopy

PI = np.pi


def get_markerchip_shape(
    chip_size=(8000, 4500),
    markerfield1_pos=(3000, 2000),
    markerfield2_pos=(5000, 2000),
    bondpads_x1=900,
    bondpads_x2=4070,
    bondpad_offset1=200,
    bondpad_offset2=100,
    mask1=1,
    mask2=2,
    res_bias_markers=False,
):
    shape = nanogds.Shape()
    # for layer 1
    shape.add(
        helpers.MarkersInCorners(
            chip_size=chip_size,
            marker_size=100,
            marker_offset=(500, 500),
            flip=False,
            correction=1,
            layer=mask1,
        ),
        add_refs=True,
    )
    # for layer 2
    angle = nanogds.Angle(25, 300, correction=1.0, layer=mask2).translate(25, 25)
    shape.add(angle, position=(0, 0), angle=0)
    shape.add(angle, position=(chip_size[0], 0), angle=PI / 2)
    shape.add(angle, position=(chip_size[0], chip_size[1]), angle=PI)
    shape.add(angle, position=(0, chip_size[1]), angle=-PI / 2)
    shape.add(
        helpers.MarkersInCorners(
            chip_size=chip_size,
            marker_size=100,
            marker_offset=(400, 400),
            flip=True,
            correction=1,
            layer=mask2,
        ),
        add_refs=True,
    )
    # # Left Marker Field
    f_left = helpers.get_marker_field(
        size=80 * 7,
        pitch=80,
        connection_sides=["left", "bottom"],
        correction=0.75,
        layer=mask1,
    )
    shape.add(f_left, position=markerfield1_pos, add_refs=True, counter=1)
    # Right Marker Field
    f_right = helpers.get_marker_field(
        size=80 * 7,
        pitch=80,
        connection_sides=["bottom", "right"],
        flip=True,
        correction=0.75,
        layer=mask1,
    )
    shape.add(f_right, position=markerfield2_pos, add_refs=True, counter=2)
    # if res_bias_markers:
    #     markers = nanogds.MarkerField(
    #         5, 2, 2, 600, correction=1, pitchy=560, layer=mask1
    #     )
    #     markers.add_corners()
    #     shape.add(markers, position=(4200, 1640))

    # # # Marker Field fo Focussing
    # f_focus = nanogds.MarkerField(5, 8, 8, 50, layer=mask1)
    # shape.add(f_focus, position=(400, 200))
    # shape.add(f_focus, position=(8250, 200))
    # # Leads Left

    bondpads_1, bondpads_2 = helpers.get_bondpads_coordinates(
        distance_to_edge=500, p1_bottom=bondpads_x1, p2_bottom=bondpads_x2, offset=300
    )
    intermediate = helpers.get_intermediate_points(
        p1_bottom=bondpads_x1 + bondpad_offset1,
        p2_bottom=bondpads_x2 - bondpad_offset2,
        slope_bottom=0,
        offset_bottom=1150,
    )
    final_1, final_2 = helpers.get_final_points(
        shape.points, offset1_left=0, offset1_bottom=0, slope_left=70, slope_bottom=0,
    )
    leads = nanogds.LeadRow(
        [bondpads_1, bondpads_2, intermediate, final_1, final_2],
        [150, 150, 10, 10, 10],
        layer=mask1,
        layer_bondpad=mask2,
    )
    shape.add(leads)
    # Leads Right
    leads.mirror([0, 1])
    shape.add(leads, position=[chip_size_x, 0])

    # Numbers
    shape.add(
        helpers.write_numbers(
            bondpad_coords=bondpads_1, chip_width=chip_size_x, layer=mask1, offset1=60
        )
    )
    return shape


def save_single_design(save_name, shape):
    lib = nanogds.GDS()
    lib.add("MARKERCHIP", shape)
    lib.save(f"{save_name}")


if __name__ == "__main__":

    chip_size_x = 9000
    chip_size_y = 5000

    params_v1 = {
        "chip_size": (chip_size_x, chip_size_y),
        "markerfield1_pos": (4000, 3000),
        "markerfield2_pos": (5000, 2000),
        "bondpad_offset1": 200,
        "bondpad_offset2": -50,
    }
    params_v2 = {
        "chip_size": (chip_size_x, chip_size_y),
        "markerfield1_pos": (3500, 2000),
        "markerfield2_pos": (5500, 2000),
        "bondpad_offset1": 200,
        "bondpad_offset2": 100,
    }

    markerchip_v1_shape = get_markerchip_shape(**params_v1)
    markerchip_v2_shape = get_markerchip_shape(**params_v2)

    # # invert
    # markerchip_v1_shape.add(
    #     nanogds.Rectangle(chip_size_x, chip_size_y, layer=1), operation="xor"
    # )
    # markerchip_v1_shape.add(
    #     nanogds.Rectangle(chip_size_x, chip_size_y, layer=2), operation="xor"
    # )
    # markerchip_v2_shape.add(
    #     nanogds.Rectangle(chip_size_x, chip_size_y, layer=1), operation="xor"
    # )
    # markerchip_v2_shape.add(
    #     nanogds.Rectangle(chip_size_x, chip_size_y, layer=2), operation="xor"
    # )

    # ################
    # ################
    # ################

    print(markerchip_v1_shape.points)

    save_single_design("markerchip_variantA", markerchip_v1_shape)
    save_single_design("markerchip_variantB", markerchip_v2_shape)

    wafer = nanogds.MaskTemplate(template="wafer_template_4x8mm")

    base_name = "1"

    refs = [ref.ref_cell.name for ref in wafer._lib.cells["Template"].references]
    for i, ref in enumerate(refs[1:89]):
        name = base_name + "A" + str(i + 1)
        shape = deepcopy(markerchip_v1_shape)
        shape.add(
            gdspy.Text(name, 300), position=(1000, 4100), layer=2, operation="xor"
        )
        wafer.add_reference("MARKERCHIP_V1_" + ref, shape.shapes, ref)
    for i, ref in enumerate(refs[89:]):
        name = base_name + "B" + str(i + 1)
        shape = deepcopy(markerchip_v2_shape)
        shape.add(gdspy.Text(name, 300), position=(1000, 4100), layer=2)
        wafer.add_reference("MARKERCHIP_V2_" + ref, shape.shapes, ref)

    wafer.write("markerchip_wafer")
