# shapely_ext
It's a shapely extension package for shapely user.
shapely_ext provides lots of magic util based on shapely, including interpolate, mesh, space explore,
 angle and decomposition
 
## install
`pip install shapely_ext`

## catalog
### project
```python
projector = Projector(geom=shapely_object, projecting_vector=vector2d_object)
projection = projector.project_onto(other_geom=other_shapely_object)
```
for polygon projecting onto polygon, projection might be a lineString or None
if one of these two objects be Point, projection might be a point or None

## TODO
1. write a tutorial
2. refactor space explorer
3. implement a magic snap function
4. implement filling util
5. implement cutting util
6. how to get mid line of gap between several big polygons
