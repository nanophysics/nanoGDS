# myGDS

Python package for designing simple GDS shapes building on `gdspy`.

## Install

```
cd mygds
python setup.py install
```

## Example

The `myGDS` base class `Shape` holds a generic `gdspy.PolygonSet` object and extends it with a set of reference points. Its method `add(...)` implements a boolean XOR operation with a new element, either a `mygds.Shape` or `gdspy.PolygonSet`, including the ability to add it at a given reference point.

```python
import mygds
import gdspy

shape = mygds.Shape()
shape.add(mygds.Rectangle(2, 3))

shape.add(mygds.Rectangle(4, 5), position=(10, 10), angle=45)

```

The reference points of the shape are store in the attribute `points`. Predefined `mygds` shapes come with reference points like *ORIGIN* or *TOPRIGHT*, etc. When adding predefined shapes to a bare `Shape` object, the user can specify if the reference points of the added shape should be inherited. 

```python
shape.add(mygds.Rectangle(2, 3), add_refs=True, counter=1)
print(shape.points)

>>> {'ORIGIN': array([0, 0]), 'RECTANGLE #1 TOPRIGHT': array([2, 3])}

shape.add(
    mygds.Rectangle(3, 4), 
    position=shape.points["RECTANGLE #1 TOPRIGHT"], 
    add_refs=True, 
    counter=2
)

>>> {'ORIGIN': array([0, 0]), 'RECTANGLE #1 TOPRIGHT': array([2, 3]), 'RECTANGLE #2 TOPRIGHT': array([5, 7])}
```

