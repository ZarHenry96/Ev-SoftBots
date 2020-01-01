from __future__ import division
import math


class Obstacle(object):
    """Base class for obstacle."""

    def __init__(self, diameter_x, diameter_y, env_size, height, prim_type=0, alfa=1):
        self.diameter_x = diameter_x/2
        self.diameter_y = diameter_y/2
        self.height = height

        self.walls = []

        self.walls.append({
            "X": ((env_size[0]-diameter_x)/2)/env_size[0],
            "Y": ((env_size[1]-diameter_y)/2)/env_size[1],
            "Z": 0,
            "dX": 1/env_size[0],
            "dY": diameter_y/env_size[1],
            "dZ": height/env_size[2]
        })

        self.walls.append({
            "X": ((env_size[0] - diameter_x) / 2) / env_size[0],
            "Y": (env_size[1] - (env_size[1] - diameter_y) / 2 - 1) / env_size[1],
            "Z": 0,
            "dX": diameter_x / env_size[0],
            "dY": 1 / env_size[1],
            "dZ": height / env_size[2]
        })

        self.walls.append({
            "X": (env_size[0] - (env_size[0]-diameter_x)/2 -1 ) / env_size[0],
            "Y": ((env_size[1] - diameter_y) / 2) / env_size[1],
            "Z": 0,
            "dX": 1 / env_size[0],
            "dY": diameter_y / env_size[1],
            "dZ": height / env_size[2]
        })

        self.walls.append({
            "X": ((env_size[0] - diameter_x) / 2) / env_size[0],
            "Y": ((env_size[1] - diameter_y) / 2) / env_size[1],
            "Z": 0,
            "dX": diameter_x / env_size[0],
            "dY": 1 / env_size[1],
            "dZ": height / env_size[2]
        })

        self.prim_type = prim_type
        self.alfa = alfa

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)


'''
for w in obst.walls:
    print()
    print("<X>" + str(w["X"])+ "</X>")
    print("<Y>" + str(w["Y"]) + "</Y>")
    print("<Z>" + str(w["Z"]) + "</Z>")
    print("<dX>" + str(w["dX"]) + "</dX>")
    print("<dY>" + str(w["dY"]) + "</dY>")
    print("<dZ>" + str(w["dZ"]) + "</dZ>")
'''
