#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image
import numpy as np
import cv2
import math
import operator

from anhdh.solve.original.Edge import Edge
from anhdh.solve.TypeEdge import *
from anhdh.solve.original import preprocessing

from anhdh.solve.original.Edge import Edge

class Piece(object):
    def __init__(self, img_path, piecenum, total, img_cnt):
        
        self.img_path = img_path
        self.image = cv2.imread(img_path)
        self.image_pillow = Image.open(img_path).convert("RGBA")
        self.width, self.height, self.channels = self.image.shape
        self.piecenum = piecenum
        self.img_cnt = img_cnt
        self.init_side()
        self.pos_origin_x, self.pos_origin_x = None, None
        self.difference_side = [[] for i in range(4)]
        self.difference = [None for x in range(total)]
    
    def init_side(self):
        denta = 5
        denta2 = 30
        self.contour = preprocessing.get_contours(self.img_cnt)
        self.arr_hor_edge, self.arr_ver_edge = preprocessing.get_point_edge(self.contour, self.image.shape[:2])

        sideUp, sideDown,sideRight, sideLeft = [], [], [], []
        edgeUp, edgeDown, edgeRight, edgeLeft = None, None, None, None

        self.contour_pos = [item[0] for item in self.contour]
        self.contour_pos = [(x, y) for x, y in self.contour_pos]
        if len(self.arr_hor_edge) != 4:
            pts1 = sorted(self.arr_hor_edge.copy(), key=lambda x: (x[2]-x[0]), reverse=True)[0]
            pts2, pts3 = [ item for item in self.arr_hor_edge if item != pts1]
            sideUp = [ (i, pts1[1]) for i in range(pts1[0], pts1[2])]
            sideDown = preprocessing.create_array_from_2_points_hor(pts2, pts3, self.contour_pos)

            edgeUp = Edge(self.image, sideUp, Direction.UP, [pts1])
            edgeDown = Edge(self.image, sideDown, Direction.DOWN, [pts2, pts3])
            if pts1[1] >= denta2:
                sideUp, sideDown = sideDown, sideUp
                edgeUp = Edge(self.image, sideUp, Direction.UP, [pts2, pts3])
                edgeDown = Edge(self.image, sideDown, Direction.DOWN, [pts1])
            
        else:
            pts1, pts2, pts3, pts4 = self.arr_hor_edge
            sideUp = preprocessing.create_array_from_2_points_hor(pts1, pts2, self.contour_pos)
            sideDown = preprocessing.create_array_from_2_points_hor(pts3, pts4, self.contour_pos)
            edgeUp = Edge(self.image, sideUp, Direction.UP, [pts1, pts2])
            edgeDown = Edge(self.image, sideDown, Direction.DOWN, [pts3, pts4])
        
        if len(self.arr_ver_edge) != 4:
            pts1 = sorted(self.arr_ver_edge.copy(), key=lambda x: (x[3]-x[1]), reverse=True)[0]
            arr = [ item for item in self.arr_ver_edge if item != pts1]
            pts2, pts3 = arr

            sideLeft = [ (pts1[0], i) for i in range(pts1[1], pts1[3])]
            sideRight = preprocessing.create_array_from_2_points_ver(pts2, pts3, self.contour_pos)

            edgeLeft = Edge(self.image, sideLeft, Direction.LEFT, [pts1])
            edgeRight = Edge(self.image, sideRight, Direction.RIGHT, [pts2, pts3])
            if pts1[0] >= denta2:
                sideLeft, sideRight = sideRight, sideLeft
                edgeLeft = Edge(self.image, sideLeft, Direction.LEFT, [pts2, pts3])
                edgeRight = Edge(self.image, sideRight, Direction.RIGHT, [pts1])
        else:
            pts1, pts2, pts3, pts4 = self.arr_ver_edge
            sideLeft = preprocessing.create_array_from_2_points_ver(pts1, pts2, self.contour_pos)
            sideRight = preprocessing.create_array_from_2_points_ver(pts3, pts4, self.contour_pos)
            edgeLeft = Edge(self.image, sideLeft, Direction.LEFT, [pts1, pts2])
            edgeRight = Edge(self.image, sideRight, Direction.RIGHT, [pts3, pts4])

        self.side = [sideUp, sideRight, sideDown, sideLeft]
        self.edge = [edgeUp, edgeRight, edgeDown, edgeLeft]
    def check_has_type(self, position, typeEdge: TypeEdge):
        current = self.edge
        return current[position].typeEdge == typeEdge

    def check_type(self, position, typeEdge: TypeEdge):
        current = self.edge
        if current[position].typeEdge == typeEdge:
            for i in range(len(current)):
                if i == position:  continue
                if current[i].typeEdge == typeEdge:
                    return False
            return True
        else:
            return False
        
    def check_type_2(self, positions, typeEdge):
        for pos in positions:
            if not self.check_has_type(pos, typeEdge): 
                return False
        current = self.edge
        for i in range(len(current)):
            if i in positions: continue
            if current[i].typeEdge == typeEdge:
                return False
        return True

    def cut(self):
        x_left, y_left_1 = sorted(self.side[3], key=lambda x: x[0], reverse=True)[0]
        x_down_1, y_down = sorted(self.side[2], key=lambda x: x[1])[0]
        y_up = self.edge[0].points[0][1]
        x_right = self.edge[1].points[0][0]
        new_img = self.image[y_up:y_down, x_left:x_right]
        self.arr_cut_img = [(y_up, y_down), (x_left, x_right)]
        self.mini_img = new_img

    def make_origin_pos(self, x_avg, y_avg):
        (y_up, y_down), (x_left, x_right) = self.arr_cut_img
        self.pos_origin_x = x_avg - x_left
        self.pos_origin_y = y_avg - y_up


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