import nanogds
import gdspy
import numpy as np
import helpers

PI = np.pi


def save_single_design(save_name, shape):
    lib = nanogds.GDS()
    lib.load_gds("Markerchip Variant B", "markerchip_variant_B.gds")
    lib.add("Resonator", shape)
    lib.save(f"designs/{save_name}")


if __name__ == "__main__":

    RESONATOR_MEANDER = 150  # total resonator length 9053 um

    MAPPING = {
        "B": [3, 4, 5, 6],
        "C": [7, 8, 9, 10],
        "D": [11, 12, 13, 14],
        "E": [15, 16, 17, 18],
    }

    mask = nanogds.MaskTemplate("mask_template")

    ### A1      ---     resonator only
    shape = helpers.get_resonator_shape(
        resonator_meander=RESONATOR_MEANDER,
        finger_length=0,
        finger_gap=6,
        extend_ground=True,
        add_tap1=False,
        add_center_tap=False,
        add_tap2=False,
    )
    mask.add_reference("A1_SHAPE", shape.shapes, "A1")
    save_single_design("A1", shape)

    ### A2      ---     resonator with gate taps
    shape = helpers.get_resonator_shape(
        resonator_meander=RESONATOR_MEANDER,
        finger_length=0,
        finger_gap=6,
        extend_ground=True,
        add_tap1=True,
        add_tap2=True,
        add_center_tap=False,
    )
    mask.add_reference("A2_SHAPE", shape.shapes, "A2")
    save_single_design("A2", shape)

    ### A3      ---     resonator with gate and center taps
    shape = helpers.get_resonator_shape(
        resonator_meander=RESONATOR_MEANDER,
        finger_length=0,
        finger_gap=6,
        extend_ground=True,
        add_tap1=True,
        add_tap2=True,
        add_center_tap=True,
    )
    mask.add_reference("A3_SHAPE", shape.shapes, "A3")
    save_single_design("A3", shape)

    ### A4      ---     resonator only
    shape = helpers.get_resonator_shape(
        resonator_meander=RESONATOR_MEANDER,
        finger_length=0,
        finger_gap=6,
        extend_ground=True,
        add_tap1=True,
        add_center_tap=True,
        add_tap2=True,
        add_ground_connection=True,
    )
    mask.add_reference("A4_SHAPE", shape.shapes, "A4")
    save_single_design("A4", shape)

    ### COLUMNS B - E       ---     variation of different finger lengths (see MAPPING)
    for column, lengths in MAPPING.items():
        for split, length in zip([f"{column}{i+1}" for i in range(4)], lengths):
            shape = helpers.get_resonator_shape(
                resonator_meander=RESONATOR_MEANDER,
                finger_length=length,
                finger_gap=3,
                extend_ground=True,
                add_tap1=True,
                add_tap2=True,
                add_center_tap=True,
            )
            mask.add_reference(f"{split}_SHAPE", shape.shapes, split)
            save_single_design(split, shape)

    ### write mask
    mask.write("MASK")
