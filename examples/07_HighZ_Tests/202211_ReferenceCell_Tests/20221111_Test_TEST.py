import nanogds
import gdspy
import numpy as np
import helpers
from copy import deepcopy, Error
from scipy.special import ellipk
from gdspy.library import CellReference, CellArray

PI = np.pi

SAVENAME = "20221031_Test"


#def save_single_design(save_name, shape):
#    lib = nanogds.GDS()
#    lib.add("TEST", shape)
#    lib.save(f"{save_name}")


if __name__ == "__main__":

    lib = nanogds.GDS()
    
#    R1 = gdspy.Rectangle((-0.5, -0.5), (0.5, 0.5))
#    
#    rectangle = gdspy.Cell("NEW")
#    rectangle.add(R1)
#
#    # create new cell with reference to rectangle cell
##    device = gdspy.Cell("DEVICE")
##    ref1 = gdspy.CellReference(rectangle, (4,1), magnification=0.5)
##    ref2 = gdspy.CellReference(rectangle, (1,4), magnification=0.5, rotation=90)
##    device.add([ref1,ref2])
#
#    # create new cell with an array referencing to rectangle cell
#    main = gdspy.Cell("MAIN")
#    main.add(gdspy.CellArray(rectangle, 8, 4, (2, 2)))
    
    R1 = gdspy.Rectangle((-0.5, -0.5), (0.5, 0.5))
    
    rectangle = gdspy.Cell("RECTANGLE")
    rectangle.add(R1)
    
    
    hole_area = gdspy.Rectangle((100,100),(400,200))
    
    chip_x = 801
    chip_y = 401
    hole_spacing = 2*1
    x = np.arange(0,chip_x,hole_spacing)
    y = np.arange(0,chip_y,hole_spacing)
    
    x_array, y_array = np.meshgrid(x,y)
#    print(array)
    position = np.array([x_array.ravel(), y_array.ravel()]).T
    
    print(position)
    
    
    
    checking_array = np.asarray([[-hole_spacing,-hole_spacing],[-hole_spacing,hole_spacing], [hole_spacing,-hole_spacing], [hole_spacing,hole_spacing]])
    
    pos_checking_array = np.asarray([pos + checking_array for pos in position])
    
    result = gdspy.inside(pos_checking_array, hole_area, short_circuit='all')


    holes_cell = gdspy.Cell("HOLES")
    for i in range(len(result)):
        if result[i]:
            holes_cell.add(gdspy.CellReference(rectangle, origin = (position[i][0],position[i][1])))
            
    
    
#    for i in range(len(x_array)):
#        print(position[i][0])
    
    #decision_array = np.array()


    lib.add("TESTTEST", holes_cell)
    lib.save("20221111_TESTHOLES")
    
    
    #save_single_design(SAVENAME, final)
    
    
    '''
    p4 = gdspy.Round((0, 0), 2.5, number_of_points=6)
    # Create a cell with a component that is used repeatedly
    contact = gdspy.Cell("CONTACT")
    contact.add([p4])

    # Create a cell with the complete device
    device = gdspy.Cell("DEVICE")
    # Add 2 references to the component changing size and orientation
    ref1 = gdspy.CellReference(contact, (3.5, 1), magnification=0.25)
    ref2 = gdspy.CellReference(contact, (1, 3.5), magnification=0.25, rotation=90)
    device.add([ref1, ref2])

    # The final layout has several repetitions of the complete device
    main = gdspy.Cell("MAIN")
    main.add(gdspy.CellArray(device, 3, 2, (6, 7)))
    
    
    device = gdspy.Cell("DEVICE")
    device.add(gdspy.Round((0, 0), 2, tolerance=0.01))
    
    # The final layout has several repetitions of the complete device
    main = gdspy.Cell("MAIN")
    main.add(gdspy.CellArray(device, 3, 2, (6, 7)))
    
    # save single design
    save_single_design(SAVENAME, main)
    '''
