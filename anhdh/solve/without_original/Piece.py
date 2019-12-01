#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image
import numpy as np
import cv2
import math
import operator

from anhdh.solve.without_original.Edge import Edge
from anhdh.solve.TypeEdge import *

class Piece(object):
    def __init__(self, img_path, piecenum,total, img_cnt):
        
        self.img_path = img_path
        self.image = cv2.imread(img_path)
        self.image_pillow = Image.open(img_path).convert("RGBA")
        self.width, self.height, self.channels = self.image.shape
        self.piecenum = piecenum
        self.img_cnt = img_cnt

        self.sideUp = []
        self.sideRight = []
        self.sideDown = []
        self.sideLeft = []

        self.edgeUp, self.edgeDown, self.edgeLeft, self.edgeRight = None, None, None,None
        self.init_side()

        self.edges = [self.edgeUp, self.edgeRight, self.edgeDown, self.edgeLeft]

        self.difference = [None for x in range(total)]
        
        self.difference2 = [None for x in range(total)]

        self.neighbors = [None for x in range(4)]

        self.difference_side = [[] for i in range(4)]

        self.difference_side2 = [[] for i in range(4)]

        cv2.imwrite(f"./test/{self.piecenum}.png", self.image)
        # if piecenum == 67:
        #     print(self.edgeUp.typeEdge, self.edgeLeft.typeEdge)
        #     cv2.imwrite(f"a.png", self.image)

    def init_side(self):
        denta =  5
        imgray = cv2.cvtColor(self.img_cnt ,cv2.COLOR_BGR2GRAY)
        ret,thresh = cv2.threshold(imgray,20,255,0)
        _, contours, hier = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        contours = sorted(contours, key=lambda cnt: len(cnt))
        self.contour = contours[0]

        # cv2.drawContours(self.image,contours,-1,(255,255,255),1)
        # cv2.imwrite("test.png", self.image)

        arr_x = {}
        arr_y = {}
        x1, x2, y1, y2 = self.get_max()
        

        ############# side right
        x1_y1, x1_y2 = self.get_min_max_height(x1)
        point1 = (x1, x1_y1)
        point2 = (x1, x1_y2)

        min_height = point1[1]
        max_height = point2[1]
        for i in range(len(self.contour)):
            x, y = self.contour[i][0]
            if (y <= max_height and y >= min_height and x >= self.width*2/3):
                self.sideRight.append((y, x))
                # self.image[y][x] = np.asarray([0, 0,  255])
        

        ############# side left
        x2_y1, x2_y2 = self.get_min_max_height(x2)
        point3 = (x2, x2_y1)
        point4 = (x2, x2_y2)

        min_height = point3[1]
        max_height = point4[1]
        from itertools import chain
        arr_delete_1 = [ [ (h1, j)for j in range(1, self.width)] for h1 in chain(range(min_height -2, min_height), range(min_height +1 , min_height +2))]
        arr_delete_2 = [ [ (h1, j)for j in range(self.width)] for h1 in chain(range(max_height -2, max_height), range(max_height +1 , max_height -2))]



        for i in range(len(self.contour)):
            x, y = self.contour[i][0]
            if (y <= max_height - 1 and y >= min_height + 1 and x <= self.width*1/3 - 10):
                self.sideLeft.append((y, x))
                self.image[y][x] = np.asarray([255, 255,  255])
        

        ############# side down
        y1_x1, y1_x2 = self.get_min_max_width(y1)
        point5 = (y1_x1, y1)
        point6 = (y1_x2, y1)

        min_width = point5[0]
        max_width = point6[0]

        (r, g, b)  = self.image[0][0]

        for i in range(len(self.contour)):
            x, y = self.contour[i][0]
            if((r, g, b) == (0, 0, 0)):
                if (x <= max_width and x >= min_width and y >= self.height*2/3):
                    self.sideDown.append((y, x))
            else:
                if (x <= max_width and x >= min_width and y >= self.height/2):
                    self.sideDown.append((y, x))
                # self.image[y][x] = np.asarray([255, 255,  255])
        

        ############# side up
        y2_x1, y2_x2 = self.get_min_max_width(y2)
        point7 = (y2_x1, y2)
        point8 = (y2_x2, y2)
        
        min_width = point7[0]
        max_width = point8[0]
        for i in range(len(self.contour)):
            x, y = self.contour[i][0]
            if (x <= max_width and x >= min_width and y <= point7[1]):
                self.sideUp.append((y, x))
                # self.image[y][x] = np.asarray([255, 255,  255])


        ############ side left

        min1, max1 = point1[1], point2[1]
        for (y, x) in self.sideRight[:]:
            if (y, x) in self.sideUp or (y, x) in self.sideDown:
                if x != point1[0]:
                    if(abs(y-min1) <= denta  or abs(y-max1) <= denta):
                        self.sideRight.remove((y, x))
                        self.image[y][x] = np.asarray([255, 255,  255])

        ############ side right

        min1, max1 = point3[1], point4[1]

        for (y, x) in self.sideLeft[:]:
            if (y, x) in self.sideUp or (y, x) in self.sideDown:
                if x != point3[0]:
                    if(abs(y-min1) <= denta  or abs(y-max1) <= denta):
                        self.sideLeft.remove((y, x))

        ############ side up

        min1, max1 = point7[0], point8[0]

        for (y, x) in self.sideUp[:]:
            if (y, x) in self.sideRight or (y, x) in self.sideLeft:
                if y != point5[1]:
                    if(abs(x-min1) <= denta  or abs(x-max1) <= denta):
                        self.sideUp.remove((y, x))

        ############ side down

        min1, max1 = point5[0], point6[0]

        for (y, x) in self.sideDown[:]:
            if (y, x) in self.sideRight or (y, x) in self.sideLeft:
                if y != point5[1]:
                    # if(abs(x-min1) <= denta  or abs(x-max1) <= denta):                       
                    self.sideDown.remove((y, x))
                            

        # for (y, x) in self.sideDown:
        #     self.image[y][x] = np.asarray([0, 0,  255])

        self.edgeRight = Edge(self.image, self.sideRight, Direction.RIGHT, point1,point2)
        self.edgeLeft = Edge(self.image, self.sideLeft, Direction.LEFT, point3,point4, debug=True)
        self.edgeDown = Edge(self.image, self.sideDown, Direction.DOWN, point5,point6)
        self.edgeUp = Edge(self.image, self.sideUp, Direction.UP, point7,point8)
        # cv2.line(self.image,point7,point8,(0,0,255),1)

    def get_min_max_height(self, x_):
        arr_y = []
        for i in range(len(self.contour)):
            x, y = self.contour[i][0]
            if(x_ == x):
                arr_y.append(y)
        sorted_y = sorted(arr_y)
        return sorted_y[0], sorted_y[-1]

    def get_min_max_width(self, y_):
        arr_x = []
        for i in range(len(self.contour)):
            x, y = self.contour[i][0]
            if(y_ == y):
                arr_x.append(x)
        sorted_x = sorted(arr_x)
        return sorted_x[0], sorted_x[-1]

    def get_max(self):
        arr_x = {}
        arr_y = {}
        for i in range(len(self.contour)):
            x, y = self.contour[i][0]
            if(x not in arr_x.keys()):
                arr_x[x] = 0
            if(y not in arr_y.keys()):
                arr_y[y] = 0
            arr_x[x] += 1
            arr_y[y] += 1
        sorted_x = sorted(arr_x.items(), key=operator.itemgetter(1), reverse=True)
        sorted_y = sorted(arr_y.items(), key=operator.itemgetter(1), reverse=True)
        x1, x2 = sorted(sorted_x[:2], key=lambda x: x[0], reverse=True)
        y1, y2 = sorted(sorted_y[:2], key=lambda x: x[0], reverse=True)

        return x1[0], x2[0], y1[0], y2[0]

    def init_different_side(self, except_piece=[]):
        for idx in range(len(self.difference)):
            if idx in except_piece: continue
            arr_diff = self.difference[idx]
            if(arr_diff is None): continue
            for diff, direction in arr_diff:
                self.difference_side[direction].append((diff, idx))
                # if  diff <  1000:
                    # self.difference_side[direction].append((diff, idx))
        for i in range(4):
            self.difference_side[i] = sorted(self.difference_side[i])

    def init_different_side2(self, except_piece=[]):
        for idx in range(len(self.difference2)):
            if idx in except_piece: continue
            arr_diff = self.difference2[idx]
            if(arr_diff is None): continue
            for diff, direction in arr_diff:
                self.difference_side2[direction].append((diff, idx))
                # if  diff <  1000:
                    # self.difference_side2[direction].append((diff, idx))
        for i in range(4):
            self.difference_side2[i] = sorted(self.difference_side2[i])