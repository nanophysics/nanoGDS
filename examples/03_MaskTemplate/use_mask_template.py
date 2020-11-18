import nanogds
import string

if __name__ == "__main__":

    mask = nanogds.MaskTemplate("mask_template")

    letters = string.ascii_uppercase

    for i in range(10):
        for j in range(6):
            shape = nanogds.Shape()
            shape.add(nanogds.Rectangle((j + 1) * 1500, 500 * (i + 1)))
            mask.add_reference(
                f"{letters[i]}{j+1}_SHAPE", shape.shapes, f"{letters[i]}{j+1}"
            )

    mask.write("test")
