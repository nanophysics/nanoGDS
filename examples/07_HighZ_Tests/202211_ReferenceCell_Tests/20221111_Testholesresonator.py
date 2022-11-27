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
GROUND_OFFSET = 20
FILLET_RADIUS = 10
SAVENAME = "20221108_Test6"


#def save_single_design(save_name, shape):
#    lib = nanogds.GDS()
#    lib.add("MARKERCHIP", shape)
#    lib.save(f"{save_name}")


def get_resonator_shape(length, RESONATOR_WIDTH, coupling_length, ground_offset, tap=True, text=None):
    resonator = nanogds.CoplanarPath(RESONATOR_WIDTH, CPW_GAP, 80, ground_offset)
    resonator.segment(length, "+y")
    w = 2 * CPW_GAP + RESONATOR_WIDTH
    resonator.add_to_outer(nanogds.Rectangle(w, CPW_GAP).translate(-w / 2, -CPW_GAP))
    resonator.add_to_outer(nanogds.Rectangle(w, CPW_GAP).translate(-w / 2, length))
    resonator.add_to_ground(nanogds.Rectangle(w + 2 * ground_offset, length + 2 * ground_offset).translate(-w / 2 - ground_offset, - CPW_GAP -ground_offset))
    text = calculate_resonator_prperties(
        RESONATOR_WIDTH * 1e-6, CPW_GAP * 1e-6, length * 1e-6, coupling_length, text=text
    )
    if tap:
        tap = nanogds.CoplanarPath(3 * RESONATOR_WIDTH, CPW_GAP, 5, ground_offset)
        tap.segment(400, "+x")
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


def get_coupler_shape(coupling_length, RESONATOR_WIDTH, ground_offset, width=30):
    shape = nanogds.CoplanarShape()
    shape.combine(
        nanogds.RectangleCapacitor(width, coupling_length, CPW_GAP, ground_offset).translate(
            -width / 2 - CPW_GAP - RESONATOR_WIDTH / 2,
            -coupling_length / 2 - FEEDLINE_WIDTH / 2,
        )
    )
    shape.combine(
        nanogds.RectangleCapacitor(width, coupling_length, CPW_GAP, ground_offset).translate(
            width / 2 + CPW_GAP + RESONATOR_WIDTH / 2,
            -coupling_length / 2 - FEEDLINE_WIDTH / 2,
        )
    )
    return shape


def get_filter(width_capacitor, length_inductor, n_inductor, width_bondpad, ground_offset, capacitor_aspect=1):
    filter = (
        nanogds.RectangleCapacitor(
            width_capacitor, capacitor_aspect * width_capacitor, CPW_GAP, ground_offset
        )
        .translate(0, -capacitor_aspect * width_capacitor / 2)
        .fillet(FILLET_RADIUS)
    )
    path = nanogds.CoplanarPath(10, CPW_GAP, 100, ground_offset)
    path.segment(80, "-y")
    filter.combine(
        path, position=[0, -capacitor_aspect * width_capacitor], add_refs=True
    )
    filter.combine(
        nanogds.Inductor(2, length_inductor, CPW_GAP, n_inductor, ground_offset).rotate(PI),
        position=filter.points["COPLANARPATH END"],
        add_refs=True,
    )
    filter.combine(path, position=filter.points["INDUCTOR TOP"], add_refs=True)
    filter.combine(
        nanogds.RectangleBondpad(width_bondpad, width_bondpad, 20, ground_offset).fillet(
            FILLET_RADIUS
        ),
        position=filter.points["COPLANARPATH END"],
    )
    h = 2 * n_inductor * CPW_GAP + 16
    filter.add_to_outer(
        nanogds.Rectangle(2 * (length_inductor + CPW_GAP), h).translate(
            -length_inductor - CPW_GAP, -capacitor_aspect * width_capacitor - h - 80
        )
    )
    filter.add_to_ground(
        nanogds.Rectangle(2 * (length_inductor + CPW_GAP + ground_offset), h + 2 * ground_offset).translate(
            - length_inductor - CPW_GAP - ground_offset, -capacitor_aspect * width_capacitor - h - 80 - ground_offset
        )
    )
    return filter


if __name__ == "__main__":
    

    lib = nanogds.GDS()
    shape = nanogds.CoplanarShape(invert=True)
    
#    R1 = gdspy.Rectangle((0, 0), (1, 1))
#    
#    rectangle = gdspy.Cell("RECTANGLE")
#    rectangle.add(R1)
#    
#    holes_cell = gdspy.Cell("HOLES")
#    holes_cell.add(gdspy.CellArray(rectangle, 10, 10, (10, 10)))
    
    #Element to add needs to be either a 'Shape' or 'gdspy.PolygonSet'... How tp convert cell to shape?
    #shape.add_to_holes(holes)
    
    # very costly way to do it....
#    for i in range(401):
#        for j in range (201):
#            shape.add_to_holes(nanogds.Square(1).translate(20*i-4000,20*j-2000))
    
    ######################################

    feedline = nanogds.CoplanarShape()
    #bondpad used to be (400, 300, 10, 400..
    bondpad = nanogds.Bondpad(500, 500, 10, 400, FEEDLINE_WIDTH, CPW_GAP, GROUND_OFFSET).rotate(
        -PI / 2
    )
    path = nanogds.CoplanarPath(FEEDLINE_WIDTH, CPW_GAP, CPW_RADIUS, GROUND_OFFSET)
    path.segment(2200, "+x")
    path.turn("l")
    path.segment(200)
    path.combine(
        bondpad, position=path.points["END"], connect_point=bondpad.points["END"]
    )

    feedline.combine(path)
    feedline.combine(path.mirror([0, 1]))
    
#    print(feedline)    

    coupling_lengths = [80, 100, 80, 100, 80, 100]
    resonator_lengths = [720, 700, 660, 640, 580, 560]
    resonator_widths = [0.65, 0.65, 0.6, 0.6, 0.55, 0.55]
    text = ""
    for i in range(6):
        resonator, text = get_resonator_shape(
            resonator_lengths[i], resonator_widths[i], coupling_lengths[i], GROUND_OFFSET, tap=True, text=text
        )
        resonator.combine(
            get_filter(400, 50, 15, 400, GROUND_OFFSET).rotate(0), resonator.points["TAP END"],
        )
        feedline.combine(
            resonator,
            position=[(i - 2.5) * 800, -FEEDLINE_WIDTH / 2 - CPW_GAP],
            connect_point=resonator.points["END"],
        )
        feedline.combine(
            get_coupler_shape(coupling_lengths[i], resonator_widths[i], GROUND_OFFSET), position=[(i - 2.5) * 800, 0]
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
    
    shape.combine(feedline, position=[0, 0])

    
#    shape.combine(dc, position=[0, -150])
#
#    shape.add_to_outer(nanogds.Rectangle(540, 240).translate(-270, -170))
#    shape.add_to_outer(nanogds.Rectangle(240, 240).translate(-120 - 600, -170))
    
    #shape = shape.get_shape(verbose=True)
    
    
    # add holes to ground plane
    R1 = gdspy.Rectangle((-0.5, -0.5), (0.5, 0.5))
    
    rectangle = gdspy.Cell("RECTANGLE")
    rectangle.add(R1)
    

    chip_x = 6000
    chip_y = 4000
    hole_spacing = 2
    x = np.arange(-chip_x/2,chip_x/2,hole_spacing)
    y = np.arange(-chip_y/2,chip_y/2,hole_spacing)
    
    x_array, y_array = np.meshgrid(x,y)
#    print(array)
    position = np.array([x_array.ravel(), y_array.ravel()]).T

    checking_array = np.asarray([[-hole_spacing,-hole_spacing],[-hole_spacing,hole_spacing], [hole_spacing,-hole_spacing], [hole_spacing,hole_spacing]])
    
    pos_checking_array = np.asarray([pos + checking_array for pos in position])
    
    
    
    polygon_ground = None
    for i in range(len(feedline._ground)):
        if isinstance(feedline._ground[i], gdspy.polygon.Path):
            polygon_ground = gdspy.boolean(polygon_ground, feedline._ground[i], operation='or')
        else:
            poly = gdspy.Polygon(feedline._ground[i].polygons[0][0])
            polygon_ground = gdspy.boolean(polygon_ground, poly, operation='or')
            
            
    polygon_outer = None
    for i in range(len(feedline._outer)):
        if isinstance(feedline._outer[i], gdspy.polygon.Path):
            polygon_outer = gdspy.boolean(polygon_outer, feedline._outer[i], operation='or')
        else:
            poly = gdspy.Polygon(feedline._outer[i].polygons[0][0])
            polygon_outer = gdspy.boolean(polygon_outer, poly, operation='or')
            
    polygon_holes = gdspy.boolean(polygon_ground, polygon_outer, operation='not')
        
    
    result = gdspy.inside(pos_checking_array, polygon_holes, short_circuit='all')
    
    polygon_center = None
    for i in range(len(feedline._center)):
        if isinstance(feedline._center[i], (gdspy.polygon.Path, gdspy.FlexPath)):
            polygon_center = gdspy.boolean(polygon_center, feedline._center[i], operation='or')
        else:
            poly = gdspy.Polygon(feedline._center[i].polygons[0][0])
            polygon_center = gdspy.boolean(polygon_center, poly, operation='or')
            
    polygon_design = gdspy.boolean(polygon_outer, polygon_center, operation='not')
    
    
#    print(feedline._ground[4].polygons[0][0])
#    print(feedline._ground[5].polygons[0][0])
#    
#    test = gdspy.Polygon(feedline._ground[5].polygons[0][0])
#    polygon_ground = gdspy.boolean(feedline._ground[2], test, operation='or')
#    print(polygon_ground)

    holes_cell = gdspy.Cell("HOLES")
    for i in range(len(result)):
        if result[i]:
            holes_cell.add(gdspy.CellReference(rectangle, origin = (position[i][0],position[i][1])))


#    design = gdspy.Cell("DESIGN")
#    design.add(shape)
#            
    final = gdspy.Cell("FINAL")
#    final.add(gdspy.CellReference(design))
    final.add(polygon_design)
    final.add(gdspy.CellReference(holes_cell))


    
    #lib.add("BLA", shape)
    lib.add("TEST", final)
    lib.save("20221111_add_holes_1")
