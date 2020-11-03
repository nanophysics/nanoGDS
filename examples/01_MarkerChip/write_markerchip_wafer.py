import nanogds
import gdspy
import numpy as np
import helpers

PI = np.pi


def get_markerchip_shape(
    chip_size=(9000, 5000),
    markerfield1_pos=(3500, 2000),
    markerfield2_pos=(5500, 2000),
    intermediate_p2_bottom=3900,
    intermediate_slope_bottom=50,
    intermediate_offset_bottom=1100,
    intermediate_p2_left=1300,
    mask1=1,
    mask2=2,
    res_bias_markers=False,
):
    shape = nanogds.Shape()
    # for layer 1
    shape.add(
        helpers.MarkersInCorners(
            chip_size=chip_size,
            marker_size=50,
            marker_offset=(200, 200),
            flip=False,
            layer=mask1,
        ),
        add_refs=True,
    )
    # for layer 2
    shape.add(
        helpers.MarkersInCorners(
            chip_size=chip_size,
            marker_size=50,
            marker_offset=(250, 250),
            flip=True,
            layer=mask2,
        ),
        add_refs=True,
    )
    # # Left Marker Field
    f_left = helpers.get_marker_field(
        size=80 * 7, pitch=80, connection_sides=["left", "bottom"], layer=mask1
    )
    shape.add(f_left, position=markerfield1_pos, add_refs=True, counter=1)
    # # Right Marker Field
    f_right = helpers.get_marker_field(
        size=80 * 7,
        pitch=80,
        connection_sides=["bottom", "right"],
        flip=True,
        layer=mask1,
    )
    shape.add(f_right, position=markerfield2_pos, add_refs=True, counter=2)
    if res_bias_markers:
        markers = nanogds.MarkerField(5, 2, 2, 600, pitchy=560, layer=mask1)
        markers.add_corners()
        shape.add(markers, position=(4200, 1640))
    # # Marker Field fo Focussing
    f_focus = nanogds.MarkerField(5, 8, 8, 50, layer=mask1)
    shape.add(f_focus, position=(400, 200))
    shape.add(f_focus, position=(8250, 200))
    # # Leads Left
    bondpads_1, bondpads_2 = helpers.get_bondpads_coordinates(distance_to_edge=200)
    intermediate = helpers.get_intermediate_points(
        p2_bottom=intermediate_p2_bottom,
        slope_bottom=intermediate_slope_bottom,
        offset_bottom=intermediate_offset_bottom,
        p2_left=intermediate_p2_left,
    )
    final_1, final_2 = helpers.get_final_points(shape.points)
    leads = nanogds.LeadRow(
        [bondpads_1, bondpads_2, intermediate, final_1, final_2],
        [180, 180, 50, 10, 10],
        layer=mask1,
        layer_bondpad=mask2,
    )
    shape.add(leads)
    # Leads Right
    leads.mirror([0, 1])
    shape.add(leads, position=[9000, 0])
    # # Lead Center
    center_lead = nanogds.Lead(
        [(4500, 200), (4500, 500), (4500, 700), (4500, 1660)],
        [180, 180, 30, 10],
        layer=mask1,
        layer_bondpad=mask2,
    )
    shape.add(center_lead)
    # Numbers
    shape.add(helpers.write_numbers(bondpad_coords=bondpads_1, layer=mask1, offset1=60))
    logo_eth = helpers.get_logo("eth_logo_kurz_pos.gds").scale(scalex=1.45, scaley=1.45)
    shape.add(logo_eth, position=(3300, 4500), layer=mask1)
    logo_qsit = helpers.get_logo("QSIT_Logo.gds").scale(scalex=0.7, scaley=0.7)
    shape.add(logo_qsit, position=(4700, 4500), layer=mask1)
    return shape


def get_HF_mask(chip_size=(9000, 5000), mask1=1):
    shape = nanogds.Shape()
    # for layer 1
    shape.add(
        helpers.MarkersInCorners(
            chip_size=chip_size,
            marker_size=50,
            marker_offset=(200, 200),
            flip=False,
            layer=mask1,
        ),
        add_refs=True,
    )
    rect = nanogds.Rectangle(8600, 2000, layer=mask1)
    shape.add(rect, position=(200, 200))
    return shape


if __name__ == "__main__":

    params_v1 = {
        "markerfield1_pos": (3500, 2000),
        "markerfield2_pos": (5500, 2000),
        "intermediate_p2_bottom": 3900,
        "res_bias_markers": True,
    }
    params_v2 = {
        "markerfield1_pos": (4000, 2000),
        "markerfield2_pos": (5000, 2000),
        "intermediate_p2_bottom": 4060,
    }

    markerchip_v1_shape = get_markerchip_shape(**params_v1)
    markerchip_v2_shape = get_markerchip_shape(**params_v2)
    mask_hf = get_HF_mask()

    # ################
    # ################
    # ################

    wafer = nanogds.FourInchWafer()
    wafer.add_reference_by_columns(
        "MARKERCHIP_V1", markerchip_v1_shape.shapes, ["A", "B", "C", "D", "E"]
    )
    wafer.add_reference_by_columns(
        "MARKERCHIP_V2", markerchip_v2_shape.shapes, ["F", "G", "H", "I"]
    )
    wafer.add_reference_by_columns("HF_MASK", mask_hf.shapes, ["J"])

    wafer.write("markerchip")
