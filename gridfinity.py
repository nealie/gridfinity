# Gridfinity basic library.
# Copyright Neal Nelson, 2022

# Based on the Basic Gridfinity Boxes by "jdegs":
# https://www.printables.com/model/174715-basic-undivided-gridfinity-boxes-cadquery-customiz

import cadquery as cq
import math as maths

# Unit dimensions.
unit_width = 42
unit_height = 7
base_height = 5
corner_radius = 4

# Base dimensions.
base_chamfer_height = 1.13 / maths.sqrt(2)
base_straight_height = 1.8
top_chamfer_height = base_height - base_chamfer_height - base_straight_height

# Magnet dimensions.
magnet_diameter = 6.5
magnet_depth = 2.4
bolt_diameter = 3
bolt_depth = 3.6 + magnet_depth
magnet_distance = 26 / 2        # Distance from holes to zero axis. 26mm between holes.

def make_base(num_x=1, num_y=1, magnet_holes=True):
    """
    Make a base, replicated as many time in the x and y direction as required.
    """
    base_sk = (
        cq.Sketch()
        .rect(unit_width, unit_width)
        .vertices()
        .fillet(corner_radius)
    )

    base = (
        cq.Workplane("XY")
        .placeSketch(base_sk)
        .extrude(top_chamfer_height * maths.sqrt(2), taper=45)
        .faces(">Z").wires().toPending()
        .extrude(base_straight_height)
        .faces(">Z").wires().toPending()
        .extrude(base_chamfer_height * maths.sqrt(2), taper=45)
        .mirror(mirrorPlane="XY")
    )

    # Copy base for as many units as needed.
    base_points = [(x * unit_width, y * unit_width) for x in range(0, num_x) for y in range(0, num_y)]
    base_points.pop(0)  # Remove first element as we don't need to copy the base we already have there.
    bases = base.pushPoints(base_points).eachpoint(lambda loc: base.val().moved(loc), combine="a")

    if magnet_holes:
        points = [
            ((base_x * unit_width - magnet_distance * (1 - 2 * hole_x)), -1 * (base_y * unit_width - magnet_distance * ( 1 - 2 * hole_y)))
            for base_x in range(0, num_x) for base_y in range(0, num_y)
            for hole_x in [0, 1] for hole_y in [0, 1]
        ]

        bases = (
            bases.faces("<Z").workplane()
            .pushPoints(points)
            .cboreHole(bolt_diameter, magnet_diameter, magnet_depth, depth=bolt_depth)
        )

    return bases

def make_module(num_x=1, num_y=1, height=1, box_clearance=0.5, magnet_holes=True):
    """
    Create a basic gridfinity module.
    """

    box_x_size = unit_width * num_x - box_clearance
    box_y_size = unit_width * num_y - box_clearance

    total_height = 3.8 + unit_height * height
    wall_height = total_height - base_height

    base = make_base(num_x, num_y, magnet_holes)

    box_sk = (
        cq.Sketch()
        .rect(box_x_size, box_y_size)
        .vertices()
        .fillet(corner_radius)
    )

    box_x_pos = unit_width * (num_x - 1) / 2
    box_y_pos = unit_width * (num_y - 1) / 2

    box = (
        cq.Workplane("XY")
        .placeSketch(box_sk)
        .extrude(wall_height)
        .translate((box_x_pos, box_y_pos, 0))
    )

    trimmer = (
        cq.Workplane("XY")
        .placeSketch(box_sk)
        .extrude(-base_height - 1)
        .translate((box_x_pos, box_y_pos, 0.5))
    )

    base = trimmer.intersect(base)
    box = box.union(base)

    return box
