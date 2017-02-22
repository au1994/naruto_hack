import itertools

g = {
    '0': [(1, 2), (2, 4), (3, 6)],
    '1': [(0, 2), (2, 3), (3, 3)],
    '2': [(0, 4), (1, 3), (3, 2)],
    '3': [(0, 1), (1, 3), (2, 2)]
}

# or graph reprensentation can be

rows = 30
columns = 40  # every row has 30 racks now
height = 5
rowgap = 2
columngap = 1
initial_distance = 0
g2 = []


def distance(point1, point2):
    if (point1 == 0) and (point2 == 0):
        return 0
    elif point1 == 0:
        point2 = (point2 - 1) % (rows * columns)
        end_column = (point2 % columns) + 1
        return (abs(end_column)) * columngap + initial_distance
    elif point2 == 0:
        point1 = (point1 - 1) % (rows * columns)
        end_column = (point1 % columns) + 1
        return (abs(end_column)) * columngap + initial_distance
    else:
        point1 = (point1 - 1) % (rows * columns)
        point2 = (point2 - 1) % (rows * columns)
        dist = abs(int(point1 / columns) - int(point2 / columns)) * rowgap
        start_column = (point1 % columns) + 1
        end_column = (point2 % columns) + 1
        if dist == 0:
            dist += (abs(start_column - end_column)) * columngap
        else:
            dist += min(start_column + end_column, 2 * columns - (start_column + end_column)) * columngap
        return dist


def get_temp_adjacency_matrix():
    for x in range(0, rows * columns * height + 1):
        temp_list = []
        for y in range(0, rows * columns * height + 1):
            temp_list.append(distance(x, y))
        g2.append(temp_list)
    return g2



