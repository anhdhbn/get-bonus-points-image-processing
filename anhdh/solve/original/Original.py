#!/usr/bin/env python
# -*- coding: utf-8 -*-

from anhdh.Common import Common
import cv2
from PIL import Image
import glob
import numpy as np
import os
import math

from anhdh.solve.original import utilities
from anhdh.solve.original.Piece import Piece
from anhdh.solve.Solver import Solver
from anhdh.solve.original.drawmatrix import draw_matrix

class Original(Solver):
    def __init__(self, img_path):
        Solver.__init__(self, img_path)
        self.width, self.height = self.image.shape[:2]

    def solve(self, ratio=0.99):
        [piece.cut() for piece in self.listsubimage]

        gray_img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        img = self.image.copy()

        for piece in self.listsubimage:
            x_avg, y_avg = self.match_image(gray_img, piece.mini_img, ratio)
            piece.make_origin_pos(x_avg, y_avg)
        temp = self.listsubimage.copy()
        temp = sorted(temp, key=lambda x: x.pos_origin_y)
        for i in range(self.num_vertical):
            temp2 = temp[i*self.num_horizontal:(i+1)*self.num_horizontal]
            temp2 = sorted(temp2, key=lambda x: x.pos_origin_x)
            for idx, item in enumerate(temp2):
                self.matrix[i][idx] = item.piecenum

        draw_matrix(self.matrix, self.listsubimage)
    

    def match_image(self, gray_image_origin, subimage, ratio):
        template = cv2.cvtColor(subimage, cv2.COLOR_BGR2GRAY)
        w, h = template.shape[::-1]
        result = cv2.matchTemplate(gray_image_origin, template, cv2.TM_CCOEFF_NORMED)
        arr = self.get_arr(result, ratio)
        x_avg, y_avg = 0, 0 
        for pt in arr:
            x_avg += pt[0]
            y_avg += pt[1]
        x_avg = int(x_avg/len(arr))
        y_avg = int(y_avg/len(arr))
        return x_avg, y_avg
        
    def get_arr(self, result, ratio):
        loc = np.where(result >= ratio)
        arr = list(zip(*loc[::-1]))
        while len(arr) == 0:
            ratio = ratio - 0.05
            loc = np.where(result >= ratio)
            arr = list(zip(*loc[::-1]))
        return arr