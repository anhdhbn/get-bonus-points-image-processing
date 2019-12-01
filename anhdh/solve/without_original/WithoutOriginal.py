#!/usr/bin/env python
# -*- coding: utf-8 -*-

from anhdh.solve.Solver import Solver
from anhdh.solve.without_original.Pieces import Pieces
from anhdh.solve.TypeEdge import TypeEdge, Direction
from anhdh.solve.without_original.diff import DiffRGB,DiffLab
from anhdh.solve.without_original import utilities
from anhdh.solve.without_original import matrix_creator
from anhdh.solve.original.drawmatrix import draw_matrix
from PIL import Image
import glob
import cv2
import numpy as np
from itertools import permutations 
import os
import time
import itertools

class WithoutOriginal(Solver):
    def __init__(self, img_path):
        Solver.__init__(self, img_path)
        self.matrix = np.asarray([  [-1 for j in range(self.num_horizontal)] for i in range(self.num_vertical)], dtype=int)
        self.diff_color = DiffRGB()
        self.init_4_corner()

    def init_4_corner(self):
        for piece in self.listsubimage:
            if piece.check_type_2([0, 3], TypeEdge.BORDER):
                self.matrix[0][0] = piece.piecenum
            if piece.check_type_2([0, 1], TypeEdge.BORDER):
                self.matrix[0][-1] = piece.piecenum
            if piece.check_type_2([3, 2], TypeEdge.BORDER):
                self.matrix[-1][0] = piece.piecenum
            if piece.check_type_2([1, 2], TypeEdge.BORDER):
                self.matrix[-1][-1] = piece.piecenum
    
    def find_diff_list(self, arr):
        for i in range(len(arr)):
            for j in range(i + 1, len(arr)):
                if i == j:
                    continue
                self.diff_color.piece_difference(arr[i], arr[j])

    def get_result_from_arr_piece(self, arr_piece, start, end, matrix_orented_func):
        arr = self.find_neighbors(arr_piece, start, end, matrix_orented_func)
        for i in range(1, self.horizontal - 1):
            self.matrix[0][i] = arr.matrix[0][i]

    def find_neighbors(self, list_piece, head_point, end_point, matrix_orented_func):
        self.refresh_piece_except()
        temp_list_piece = [piece.piecenum for piece in  list_piece if piece.piecenum not in self.piece_except]
        new_list_piece = list(permutations(temp_list_piece))
        new_list_piece = [ (head_point,)  + piece  + (end_point,) for piece in new_list_piece]
        arr = [ Pieces(self.listsubimage, matrix_orented_func(piece, self.num_horizontal, self.num_vertical)) for piece in new_list_piece]
        arr = sorted(arr, key=lambda x: x.total_distance)
        return arr[0]

    def refresh_piece_except(self):
        flatten = self.matrix.flatten()
        self.piece_except = [num for num in flatten if num != -1]

    def solve_border(self):
        arr_hor = [piece for piece in self.listsubimage if piece.check_has_type(0, TypeEdge.BORDER)]
        arr_hor_down = [piece for piece in self.listsubimage if piece.check_has_type(2, TypeEdge.BORDER)]
        arr_ver = [piece for piece in self.listsubimage if piece.check_has_type(3, TypeEdge.BORDER)]
        arr_ver_right = [piece for piece in self.listsubimage if piece.check_has_type(1, TypeEdge.BORDER)]

        self.find_diff_list(arr_hor)
        self.find_diff_list(arr_hor_down)
        self.find_diff_list(arr_ver)
        self.find_diff_list(arr_ver_right)

        
        arr = self.find_neighbors(arr_hor, self.matrix[0][0], self.matrix[0][-1], matrix_creator.create_matrix_hor_up)
        for i in range(1, self.num_horizontal - 1):
            self.matrix[0][i] = arr.matrix[0][i]
        
        
        arr = self.find_neighbors(arr_ver_right, self.matrix[0][-1], self.matrix[-1][-1], matrix_creator.create_matrix_ver_right)
        for i in range(1, self.num_vertical - 1):
            self.matrix[i][-1] = arr.matrix[i][-1]

        
        arr = self.find_neighbors(arr_hor_down, self.matrix[-1][0], self.matrix[-1][-1], matrix_creator.create_matrix_hor_down)
        for i in range(1, self.num_horizontal - 1):
            self.matrix[-1][i] = arr.matrix[-1][i]

        arr = self.find_neighbors(arr_ver, self.matrix[0][0], self.matrix[-1][0], matrix_creator.create_matrix_ver_left)
        for i in range(1, self.num_vertical - 1):
            self.matrix[i][0] = arr.matrix[i][0]

    def solve_ver(self):
        ver_half, hor_half = self.num_vertical/2, self.num_horizontal/2
        for i in range(1, self.num_horizontal - 1):
            arr_ver  = [[] for i in range(1, self.num_vertical - 1)]
            for j in range(1, self.num_vertical - 1):
                prev_idx =  self.matrix[j][i-1]
                prev_piece = self.listsubimage[prev_idx]
                prev_right = prev_piece.difference_side[1]
                arr_right = [ (diff, idx) for diff, idx in prev_right if idx not in self.piece_except]
                arr_ver[j - 1] = arr_right[:10]
            arr = matrix_creator.get_min_distance_matrix(arr_ver, self.matrix, i, self.listsubimage)

            draw_matrix(arr[0].matrix, self.listsubimage)
            break
            bac = ""

    def brute_force(self):
        arr_remain = [piece.piecenum for piece in self.listsubimage if piece.piecenum not in self.piece_except]
        matrix_creator.brute_force(arr_remain, self.matrix, self.listsubimage)

    def solve(self):
        self.solve_border()
        self.find_diff_list(self.listsubimage)
        [ piece.init_different_side() for piece in self.listsubimage]

        image = draw_matrix(self.matrix, self.listsubimage)
        image.save("./assets/without_original.png")