# Gridfinity battery tray generator.
# Copyright Neal Nelson 2022.

import cadquery as cq
import gridfinity

# Batteries.
AA = 14.5
AAA = 10.5
CR123 = 17
C = 26.2
D = 34.2

def tube_battery_tray(
    battery,                # Which battery size to use.
    num_x=1,                # X size in gridfinity units.
    num_y=1,                # Y size in gridfinity units.
    height=2,               # Height in gridfinity units.
    box_clearance=0.5,      # Space between this boex on the grid.
    magnet_holes=False,
    minimum_wall=1.0        # Minimum wall thickness before redeucing capacity.
):
    """
    Generate a gridfinity compatible battery tray for CR123 batteries.
    """
    clearance = 0.2
    battery_diameter = battery + clearance

    box = gridfinity.make_module(
        num_x=num_x,
        num_y=num_y,
        height=height,
        box_clearance=box_clearance,
        magnet_holes=magnet_holes
    )

    depth = gridfinity.unit_height * height - 2

    total_x_width = gridfinity.unit_width * num_x
    total_y_width = gridfinity.unit_width * num_y

    holes_x = int(total_x_width // battery_diameter)
    holes_y = int(total_y_width // battery_diameter)

    # Distribute the holes evenly.
    wall_x = (total_x_width - (battery_diameter * holes_x)) / (holes_x + 1)
    if wall_x < minimum_wall:
        holes_x -= 1
        wall_x = (total_x_width - (battery_diameter * holes_x)) / (holes_x + 1)
    hole_x_offset = (total_x_width - wall_x) / holes_x

    wall_y = (total_y_width - (battery_diameter * holes_y)) / (holes_y + 1)
    if wall_y < minimum_wall:
        holes_y -= 1
        wall_y = (total_y_width - (battery_diameter * holes_y)) / (holes_y + 1)
    hole_y_offset = (total_y_width - wall_y) / holes_y

    points = []
    x_pos = -(gridfinity.unit_width / 2) + (wall_x / 2) + (hole_x_offset / 2)
    for x in range(holes_x):
        y_pos = -(gridfinity.unit_width / 2) + (wall_y / 2) + (hole_y_offset / 2)
        for y in range(holes_y):
            points.append((x_pos, y_pos))
            y_pos += hole_y_offset
        x_pos += hole_x_offset

    box = (
        box.faces(">Z")
        .workplane()
        .pushPoints(points)
        .hole(battery_diameter, depth)
    )

    return box

if __name__ == "__main__" or __name__ == "temp":
    box = tube_battery_tray(battery=CR123, num_x=1, num_y=3)

    if __name__ != "__main__":
        show_object(box)
    else:
        cq.exporters.export(box, "battery_holder.amf")
