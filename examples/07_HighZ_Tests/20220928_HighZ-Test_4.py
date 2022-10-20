import nanogds
import gdspy
import numpy as np
import helpers
from copy import deepcopy, Error
from scipy.special import ellipk

PI = np.pi
FEEDLINE_WIDTH = 250
RESONATOR_WIDTH = 1
CPW_GAP = 4
CPW_RADIUS = 400
FILLET_RADIUS = 10
SAVENAME = "20220928_HighZ-Test_4"


def save_single_design(save_name, shape):
    lib = nanogds.GDS()
    lib.add("MARKERCHIP", shape)
    lib.save(f"{save_name}")


def get_resonator_shape(length, RESONATOR_WIDTH, coupling_length, tap=True, text=None):
    resonator = nanogds.CoplanarPath(RESONATOR_WIDTH, CPW_GAP, 80)
    resonator.segment(length, "+y")
    w = 2 * CPW_GAP + RESONATOR_WIDTH
    resonator.add_to_outer(nanogds.Rectangle(w, CPW_GAP).translate(-w / 2, -CPW_GAP))
    resonator.add_to_outer(nanogds.Rectangle(w, CPW_GAP).translate(-w / 2, length))
    text = calculate_resonator_prperties(
        RESONATOR_WIDTH * 1e-6, CPW_GAP * 1e-6, length * 1e-6, coupling_length, text=text
    )
    if tap:
        tap = nanogds.CoplanarPath(3 * RESONATOR_WIDTH, CPW_GAP, 5)
        tap.segment(1.4 * length / 2, "+x")
        tap.turn("r")
        tap.segment(80)
        resonator.combine(tap, position=[0, length / 2], add_refs=True)
        resonator.add_reference("TAP END", resonator.points["COPLANARPATH END"])
    return resonator, text


def calculate_resonator_prperties(
    w, g, l, coupling_length, epsilon=11.45, sheet_inductance=125e-12, text=None
):
    epsilon_0 = 8.854e-12
    epsilon_eff = (epsilon + 1) / 2
    mu_0 = 1.256e-6
    k = w / (w + 2 * g)
    k_prime = np.sqrt(1 - k ** 2)
    capacitance_l = 4 * epsilon_0 * epsilon_eff * ellipk(k) / ellipk(k_prime)
    inductance_l = mu_0 / 4 * ellipk(k_prime) / ellipk(k) + sheet_inductance / w
    freq = 1 / (2 * l * np.sqrt(capacitance_l * inductance_l))
    impedance = np.sqrt(inductance_l / capacitance_l)
    text += f"With w = {w * 1e6} um and s = {g * 1e6} um and l = {l * 1e6} um and coupling length = {coupling_length} um:\n"
    text += f"    - C_l: {capacitance_l} F/m\n"
    text += f"    - L_l: {inductance_l} H/m\n"
    text += f"    - Frequency: {freq * 1e-9} GHz\n"
    text += f"    - Impedance: {np.round(impedance)} Ohm\n"
    return text


def get_coupler_shape(coupling_length, RESONATOR_WIDTH, width=30):
    shape = nanogds.CoplanarShape()
    shape.combine(
        nanogds.RectangleCapacitor(width, coupling_length, CPW_GAP).translate(
            -width / 2 - CPW_GAP - RESONATOR_WIDTH / 2,
            -coupling_length / 2 - FEEDLINE_WIDTH / 2,
        )
    )
    shape.combine(
        nanogds.RectangleCapacitor(width, coupling_length, CPW_GAP).translate(
            width / 2 + CPW_GAP + RESONATOR_WIDTH / 2,
            -coupling_length / 2 - FEEDLINE_WIDTH / 2,
        )
    )
    return shape


def get_filter(width_capacitor, n_inductor, width_bondpad, capacitor_aspect=1):
    filter = (
        nanogds.RectangleCapacitor(
            width_capacitor, capacitor_aspect * width_capacitor, CPW_GAP
        )
        .translate(0, -capacitor_aspect * width_capacitor / 2)
        .fillet(FILLET_RADIUS)
    )
    path = nanogds.CoplanarPath(10, CPW_GAP, 100)
    path.segment(80, "-y")
    filter.combine(
        path, position=[0, -capacitor_aspect * width_capacitor], add_refs=True
    )
    filter.combine(
        nanogds.Inductor(2, 50, CPW_GAP, n_inductor).rotate(PI),
        position=filter.points["COPLANARPATH END"],
        add_refs=True,
    )
    filter.combine(path, position=filter.points["INDUCTOR TOP"], add_refs=True)
    filter.combine(
        nanogds.RectangleBondpad(width_bondpad, width_bondpad, 20).fillet(
            FILLET_RADIUS
        ),
        position=filter.points["COPLANARPATH END"],
    )
    h = n_inductor * (4 + 3 * CPW_GAP) + 32
    filter.add_to_outer(
        nanogds.Rectangle(200, h).translate(
            -100, -capacitor_aspect * width_capacitor - h - 80
        )
    )
    return filter


if __name__ == "__main__":

    shape = nanogds.CoplanarShape(invert=True)

    ######################################

    feedline = nanogds.CoplanarShape()
    bondpad = nanogds.Bondpad(400, 300, 10, 400, FEEDLINE_WIDTH, CPW_GAP, True).rotate(
        -PI / 2
    )
    path = nanogds.CoplanarPath(FEEDLINE_WIDTH, CPW_GAP, CPW_RADIUS)
    path.segment(2200, "+x")
    path.turn("l")
    path.segment(200)
    path.combine(
        bondpad, position=path.points["END"], connect_point=bondpad.points["END"]
    )

    feedline.combine(path)
    feedline.combine(path.mirror([0, 1]))

    coupling_lengths = [80 + i * 0 for i in range(6)]
    resonator_lengths = [650 + i * 20 for i in range(6)]
    resonator_widths = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    text = ""
    for i in range(6):
        resonator, text = get_resonator_shape(
            resonator_lengths[i], resonator_widths[i], coupling_lengths[i], tap=False, text=text
        )
#        resonator.combine(
#            get_filter(400, 15, 400).rotate(0), resonator.points["TAP END"],
#        )
        feedline.combine(
            resonator,
            position=[(i - 2.5) * 700, -FEEDLINE_WIDTH / 2 - CPW_GAP],
            connect_point=resonator.points["END"],
        )
        feedline.combine(
            get_coupler_shape(coupling_lengths[i], resonator_widths[i]), position=[(i - 2.5) * 700, 0]
        )
    with open(f"{SAVENAME}_INFO.txt", "w") as f:
        f.write(text)

    #################################
    # DC lines
#    dc = nanogds.CoplanarShape()
#    pitch = 650
#    
#    for i in range(-4, 5):
#        path = nanogds.CoplanarPath(15, 30, 0)
#        path.segment(300 - abs(i) * 50, "-y")
#        if i < 0:
#            path.turn("r")
#            path.segment(abs(i) * pitch - 50)
#            path.turn("l")
#            path.segment(abs(i) * 50 + 300)
#        elif i > 0:
#            path.turn("l")
#            path.segment(abs(i) * pitch - 50)
#            path.turn("r")
#            path.segment(abs(i) * 50 + 300)
#        else:
#            path.segment(300)
#
#        path.combine(get_filter(400, 15, 400), position=path.points["END"])
#        dc.combine(path, position=[i * 50, 0])

    shape.combine(feedline, position=[0, 250])
    
#    shape.combine(dc, position=[0, -150])
#
#    shape.add_to_outer(nanogds.Rectangle(540, 240).translate(-270, -170))
#    shape.add_to_outer(nanogds.Rectangle(240, 240).translate(-120 - 600, -170))

    shape = shape.get_shape(verbose=True)

    # save single design
    save_single_design(SAVENAME, shape)

    # ################
    # ################
    # ################

