import numpy as np
from anhdh.solve.TypeEdge import *
import math

class Edge(object):
    def __init__(self, origin_img, pixel_edge, direction, point_start, point_end, debug=False):
        self.origin_img = origin_img.copy()
        self.height, self.width = self.origin_img.shape[:2]
        self.pixel_edge = pixel_edge
        self.diection = direction
        self.point_start = point_start
        self.point_end = point_end
        self.typeEdge = None
        self.color_edge = []
        self.debug = debug
        for y, x in self.pixel_edge:
            self.color_edge.append(self.origin_img[y][x])
        self.detect_hump(origin_img)


    def detect_hump(self, origin_img):
        denta = 10
        if self.debug:
            av = ""
        if self.diection == Direction.UP:
            min_height, max_height = 100000, 0

            
            if (self.point_start[1]  >= denta):
                self.typeEdge = TypeEdge.HUMP
            else:
                for x, y in self.pixel_edge:   
                    if(x  < min_height): min_height = x
                    if(x > max_height): max_height = x
                if (max_height - denta > 0):
                    self.typeEdge = TypeEdge.REVERSE_HUMP
                else:
                    self.typeEdge = TypeEdge.BORDER
        elif self.diection == Direction.DOWN:
            min_height, max_height = 10000, 0
            
            if (self.point_start[1]  <= self.height - denta):
                self.typeEdge = TypeEdge.HUMP
            else:
                for y, x in self.pixel_edge:
                    if(y  < min_height): min_height = y
                    if(y > max_height): max_height = y
                if (self.height - min_height > denta):
                    self.typeEdge = TypeEdge.REVERSE_HUMP
                else:
                    self.typeEdge = TypeEdge.BORDER
        elif self.diection == Direction.LEFT:
            min_width, max_width = 10000, 0

            if (self.point_start[0]  >= denta ):
                self.typeEdge = TypeEdge.HUMP
            else:
                for x, y in self.pixel_edge:   
                    if(y  < min_width): min_width = y
                    if(y > max_width): max_width = y
                if (max_width > denta):
                    self.typeEdge = TypeEdge.REVERSE_HUMP
                else:
                    self.typeEdge = TypeEdge.BORDER
        else:
            min_width, max_width = 10000, 0

            if (self.point_start[0] <= self.width - denta):
                self.typeEdge = TypeEdge.HUMP
            else:
                for y, x in self.pixel_edge:   
                    if(x  < min_width): min_width = x
                    if(x > max_width): max_width = x
                if (min_width + denta < self.width):
                    self.typeEdge = TypeEdge.REVERSE_HUMP
                else:
                    self.typeEdge = TypeEdge.BORDER
        
        # for (y, x) in self.pixel_edge:
        #     if self.typeEdge == TypeEdge.BORDER: 
        #         origin_img[y][x] = np.asarray([255, 0, 0]) # blue
        #     elif self.typeEdge == TypeEdge.HUMP: 
        #         origin_img[y][x] = np.asarray([0, 255, 0]) # green
        #     elif self.typeEdge == TypeEdge.REVERSE_HUMP:                                     
        #         origin_img[y][x] = np.asarray([0, 0, 255]) # red