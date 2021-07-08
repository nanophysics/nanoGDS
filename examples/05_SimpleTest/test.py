import nanogds as nano


if __name__ == "__main__":

    lib = nano.GDS()

    # define first shape
    shape1 = nano.Shape()
    shape1.add(nano.Rectangle(100, 200), position=[-100, 0])

    # add shape to cell 'CELL1' and save as 'test.gds'
    lib.add("CELL1", shape1)
    lib.save("test")

    # load cell 'CELL1' from 'test.gds' to new library
    new_lib = nano.GDS()
    new_lib.load_gds("CELL1", "test.gds")

    # # define second shape
    shape2 = nano.Shape()
    shape2.add(nano.Rectangle(100, 200), position=[100, 0])

    # # add second shape to cell 'CELL1' and save as 'test.gds'
    new_lib.add("CELL2", shape2)
    new_lib.save("test2")

