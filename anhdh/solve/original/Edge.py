import numpy as np
from anhdh.solve.TypeEdge import *
import math

class Edge(object):
    def __init__(self, origin_img, pixel_edge, direction, points, debug=False):
        self.origin_img = origin_img
        self.height, self.width = self.origin_img.shape[:2]
        self.pixel_edge = pixel_edge
        self.diection = direction
        self.points = points
        self.typeEdge = None
        self.color_edge = []
        self.debug = debug
        for i, j in self.pixel_edge:
            self.color_edge.append(self.origin_img[j][i])
        self.detect_hump()

    def detect_hump(self):
        denta = 10       

        if len(self.points) == 1:
            self.typeEdge = TypeEdge.BORDER
        else:
            pts1, pts2 = self.points
            if self.diection == Direction.UP:
                if pts1[1] > denta:
                    self.typeEdge = TypeEdge.HUMP
                else:
                    self.typeEdge = TypeEdge.REVERSE_HUMP
            elif self.diection == Direction.RIGHT:
                if pts1[0] + denta < self.width:
                    self.typeEdge = TypeEdge.HUMP
                else:
                    self.typeEdge = TypeEdge.REVERSE_HUMP
            elif self.diection == Direction.DOWN:
                if pts1[1] + denta < self.height:
                    self.typeEdge = TypeEdge.HUMP
                else:
                    self.typeEdge = TypeEdge.REVERSE_HUMP
            elif self.diection == Direction.LEFT:
                if pts1[0]> denta :
                    self.typeEdge = TypeEdge.HUMP
                else:
                    self.typeEdge = TypeEdge.REVERSE_HUMP

        # for (y, x) in self.pixel_edge:
        #     if self.typeEdge == TypeEdge.BORDER: 
        #         self.origin_img[x][y] = np.asarray([255, 0, 0]) # blue
        #     elif self.typeEdge == TypeEdge.HUMP: 
        #         self.origin_img[x][y] = np.asarray([0, 255, 0]) # green
        #     elif self.typeEdge == TypeEdge.REVERSE_HUMP:                                     
        #         self.origin_img[x][y] = np.asarray([0, 0, 255]) # red
        