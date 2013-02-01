from housepy import science, drawing

SIZE = 500, 500
X, Y = 0, 1

brooklyn = [-73.9565, 40.7111]
manhattan = [-73.9735, 40.7697]

points = [brooklyn, manhattan]
points = [list(science.geo_project(point)) for point in points]


min_x = min([point[X] for point in points])
min_y = min([point[Y] for point in points])
points = [((point[X] - min_x), (point[Y] - min_y)) for point in points]

max_x = max([point[X] for point in points])
max_y = max([point[Y] for point in points])
factor = max(max_x, max_y)


def normalize_position(point, min_x, min_y, factor):
    point[X] -= min_x
    point[Y] -= min_y
    point[X] /= factor
    point[Y] /= factor
    return point


# for p, point in enumerate(points):
#     points[p] = normalize_position(point, min_x, min_y, factor)


points = [(point[X] / factor, point[Y] / factor) for point in points]
print points

ctx = drawing.Context(500, 500, relative=True, flip=True, margin=100)
for point in points:
    ctx.arc(*point, radius_x=10.0 / ctx.width, fill=(0., 0., 0.))
ctx.show()
ctx.image.save('test_cities.png', 'PNG')

