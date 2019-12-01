#!/usr/bin/env python
# -*- coding: utf-8 -*-

from anhdh.Common import Common
from anhdh.solve.without_original.Piece import Piece
from anhdh.solve.without_original.Pieces import Pieces
from anhdh.solve.TypeEdge import *
from anhdh.solve.without_original import utilities
from PIL import Image
import glob
import cv2
import numpy as np
from itertools import permutations 
import os
import time
import itertools


class WithoutOriginalSolver(Common):
    def __init__(self, img_path):
        Common.__init__(self, img_path)
        
        self.listsubimg_path = glob.glob(f"{self.raster_folder}/*.png")
        self.image = cv2.imread(img_path)
        self.init_sub_img()
        self.init_size_original()
        self.list_matrix_sub = []
    
    def append_list_matrix(self, matrix):
        print(len(self.list_matrix_sub))
        self.list_matrix_sub.append(matrix)

    def init_sub_img(self):
        masks_obj = utilities.read_data_to_obj(self.folder_process, "masks.json")
        pieces_obj = utilities.read_data_to_obj(self.folder_process, "pieces.json")
        
        for key in pieces_obj:
            data = pieces_obj[key]
            for key2 in masks_obj:
                data2 = masks_obj[key2]
                if ( data == data2):
                    pieces_obj[key] = (data, key2)
                    break
        # print(pieces_obj)
        self.listsubimg_path  = sorted(self.listsubimg_path, key=lambda x: self.get_id_by_path(x))
        self.listsubimage = []
        for idx, path in enumerate(self.listsubimg_path):
            name = os.path.basename(path)
            name = name.replace(".png", "")
            name = name.split("-")[2]
            temp = pieces_obj[name]
            piece = Piece(path, idx,len(self.listsubimg_path), self.crop_img(temp[1], temp[0]))
            self.listsubimage.append(piece)

    def init_size_original(self):
        self.piece_horizontal = []
        self.piece_vertical = []
        for piece in self.listsubimage:
            if ((piece.edgeUp.typeEdge == TypeEdge.BORDER) and 
                (piece.edgeRight.typeEdge != TypeEdge.BORDER) and      
                (piece.edgeDown.typeEdge != TypeEdge.BORDER) and      
                (piece.edgeLeft.typeEdge != TypeEdge.BORDER) ):
                self.piece_horizontal.append(piece)
            if ((piece.edgeLeft.typeEdge == TypeEdge.BORDER) and 
                (piece.edgeRight.typeEdge != TypeEdge.BORDER) and      
                (piece.edgeDown.typeEdge != TypeEdge.BORDER) and      
                (piece.edgeUp.typeEdge != TypeEdge.BORDER) ):
                self.piece_vertical.append(piece)
                # print(piece.edgeUp.typeEdge, piece.edgeRight.typeEdge, piece.edgeDown.typeEdge, piece.edgeLeft.typeEdge)
                # cv2.imwrite(f"./test/{vertical}.png", piece.image) 
        self.horizontal = len(self.piece_horizontal) + 2
        self.vertical = len(self.piece_vertical) + 2

        self.matrix = np.asarray([  [None for j in range(self.horizontal)] for i in range(self.vertical)])
        self.piece_except = []
        for piece in self.listsubimage:
            if ((piece.edgeUp.typeEdge == TypeEdge.BORDER) and 
                (piece.edgeLeft.typeEdge == TypeEdge.BORDER) and
                (piece.edgeRight.typeEdge != TypeEdge.BORDER) and      
                (piece.edgeDown.typeEdge != TypeEdge.BORDER)      
                 ):
                self.matrix[0][0] = piece.piecenum
                self.piece_except.append(piece.piecenum)
            if ((piece.edgeUp.typeEdge == TypeEdge.BORDER) and 
                (piece.edgeRight.typeEdge == TypeEdge.BORDER) and
                (piece.edgeLeft.typeEdge != TypeEdge.BORDER) and      
                (piece.edgeDown.typeEdge != TypeEdge.BORDER)      
                 ):
                self.piece_except.append(piece.piecenum)
                self.matrix[0][-1] = piece.piecenum
            if ((piece.edgeDown.typeEdge == TypeEdge.BORDER) and 
                (piece.edgeLeft.typeEdge == TypeEdge.BORDER) and
                (piece.edgeRight.typeEdge != TypeEdge.BORDER) and      
                (piece.edgeUp.typeEdge != TypeEdge.BORDER)      
                 ):
                self.piece_except.append(piece.piecenum)
                self.matrix[-1][0] = piece.piecenum
            if ((piece.edgeDown.typeEdge == TypeEdge.BORDER) and 
                (piece.edgeRight.typeEdge == TypeEdge.BORDER) and
                (piece.edgeLeft.typeEdge != TypeEdge.BORDER) and      
                (piece.edgeUp.typeEdge != TypeEdge.BORDER)      
                 ):
                self.piece_except.append(piece.piecenum)
                self.matrix[-1][-1] = piece.piecenum
        self.piece_horizontal.insert(0, self.listsubimage[self.matrix[0][0]])
        self.piece_horizontal.append(self.listsubimage[self.matrix[0][-1]])
        self.piece_vertical.insert(0, self.listsubimage[self.matrix[-1][0]])
        self.piece_vertical.append(self.listsubimage[self.matrix[-1][-1]])
        # self.listsubimage = [Piece(path) for path in self.listsubimg_path]

    def get_id_by_path(self, path):
        name = os.path.basename(path)
        name = name.replace(".png", "")
        name = name.split("-")[2]
        return int(name)

    def crop_img(self, name, position):
        path = os.path.join(self.folder_process, f"m-{name}.png")
        x, y, x1, y1 = position
        img = Image.open(path).convert("RGBA")
        img_cropped = img.crop((x, y, x1, y1))
        img_width, img_height = img_cropped.size
        
        for i in range(img_width):
            for j in range(img_height):
                current_color = img_cropped.getpixel((i,j))
                if(current_color != (0, 0, 0, 0)):
                    img_cropped.putpixel( (i,j), (0, 0, 255, 255))
        img_cropped = img_cropped.convert("RGB")
        img_arr = np.asarray(img_cropped)
        return img_arr[:, :, ::-1].copy()
        
    def find_diff_list(self, arr, use_rgb=True):
        for i in range(len(arr)):
            for j in range(i + 1, len(arr)):
                if i == j:
                    continue
                utilities.piece_difference(arr[i], arr[j], use_rgb)
        
    def get_piece_vertical_right(self):
        result = []
        for piece in self.listsubimage:
            if ((piece.edgeRight.typeEdge == TypeEdge.BORDER) and 
                (piece.edgeUp.typeEdge != TypeEdge.BORDER) and      
                (piece.edgeDown.typeEdge != TypeEdge.BORDER) and      
                (piece.edgeLeft.typeEdge != TypeEdge.BORDER) ):
                result.append(piece)
        result.insert(0, self.listsubimage[self.matrix[0][-1]])
        result.append(self.listsubimage[self.matrix[-1][-1]])
        return result

    def get_piece_horizontal_down(self):
        result = []
        for piece in self.listsubimage:
            if ((piece.edgeDown.typeEdge == TypeEdge.BORDER) and 
                (piece.edgeRight.typeEdge != TypeEdge.BORDER) and      
                (piece.edgeUp.typeEdge != TypeEdge.BORDER) and      
                (piece.edgeLeft.typeEdge != TypeEdge.BORDER) ):
                result.append(piece)
        result.insert(0, self.listsubimage[self.matrix[-1][0]])
        result.append(self.listsubimage[self.matrix[-1][-1]])
        return result

    def solve(self):
        # for horizontal
        # # self.find_diff_list(self.piece_horizontal)

        # test_matrix = self.matrix.copy()

        # test_matrix[0]  =  np.asarray([67, 42, 62, 48, 39, 34, 19, 32, 35, 58])
        # test_matrix[1]  =  np.asarray([51,  0,  0,  1, 33, 31, 11,  0,  9,  6])
        # test_matrix[2]  =  np.asarray([64, 14,  0,  0,  5, 47,  0,  0,  0, 26])
        # test_matrix[3]  =  np.asarray([55,  0, 57, 16, 13, 66, 15, 54,  0, 29])
        # test_matrix[4]  =  np.asarray([41, 68, 25, 50, 61,  4, 56, 36,  2, 18])
        # test_matrix[5]  =  np.asarray([30,  7, 21, 23, 28, 37,  3, 17,  0, 59])
        # test_matrix[6]  =  np.asarray([10, 65, 12, 45,  8, 52, 46, 53,  0, 43])

        # utilities.draw_matrix(test_matrix, self.listsubimage)
        # temp = test_matrix.flatten()
        # print([piece.piecenum for piece in self.listsubimage if piece.piecenum not in temp])

        utilities.piece_difference(self.listsubimage[33], self.listsubimage[31])
        start = time.time()
        self.find_diff_list(self.piece_horizontal)
        arr = self.find_neighbors(self.piece_horizontal, self.matrix[0][0], self.matrix[0][-1], self.create_matrix_hor_up, self.piece_except)
        for i in range(1, self.horizontal - 1):
            self.matrix[0][i] = arr.matrix[0][i]

        self.find_diff_list(self.get_piece_vertical_right())
        arr = self.find_neighbors(self.get_piece_vertical_right(), self.matrix[0][-1], self.matrix[-1][-1], self.create_matrix_ver_right, self.piece_except)
        for i in range(1, self.vertical - 1):
            self.matrix[i][-1] = arr.matrix[i][-1]
        

        self.find_diff_list(self.get_piece_horizontal_down())
        arr = self.find_neighbors(self.get_piece_horizontal_down(), self.matrix[-1][0], self.matrix[-1][-1], self.create_matrix_hor_down, self.piece_except)
        for i in range(1, self.horizontal - 1):
            self.matrix[-1][i] = arr.matrix[-1][i]

        self.find_diff_list(self.piece_vertical)
        arr = self.find_neighbors(self.piece_vertical, self.matrix[0][0], self.matrix[-1][0], self.create_matrix_ver_left, self.piece_except)
        for i in range(1, self.vertical - 1):
            self.matrix[i][0] = arr.matrix[i][0]
        
        


        # end = time.time()
        # print(end - start)
        


        # utilities.draw_matrix(self.matrix, self.listsubimage)

        # convert ra piece
        # sub_arr = utilities.get_arr_sub(self.matrix, self.listsubimage)
        # self.find_diff_list(self.listsubimage, True)

        # except_matrix = utilities.get_arr_except(self.matrix)

        # [ piece.init_different_side() for piece in self.listsubimage]
        # self.abc(self.matrix.copy())

        # self.create_sub_array(self.matrix.copy())

        # arr = [ Pieces(self.listsubimage, matrix) for matrix in self.list_matrix_sub]
        # arr = sorted(arr, key=lambda x: x.total_distance)

        # print(len(arr))
        # print(len(self.list_matrix_sub))
        # utilities.draw_matrix(arr[0].matrix, self.listsubimage)

        

        # self.matrix[0]  =  np.asarray([67, 42, 62, 48, 39, 34, 19, 32, 35, 58])
        # self.matrix[1]  =  np.asarray([51, None, None, None, None, None, None, None, None,  6])
        # self.matrix[2]  =  np.asarray([64, None,  None, None, None, None, None, None, None, 26])
        # self.matrix[3]  =  np.asarray([55,  None,  None, None, None, None, None, None, None, 29])
        # self.matrix[4]  =  np.asarray([41, None,  None, None, None, None, None, None, None, 18])
        # self.matrix[5]  =  np.asarray([30,  None,  None, None, None, None, None, None, None, 59])
        # self.matrix[6]  =  np.asarray([10, 65, 12, 45,  8, 52, 46, 53,  0, 43])
        self.find_diff_list(self.listsubimage, True)
        [ piece.init_different_side() for piece in self.listsubimage]
        self.get_best(self.matrix)
        utilities.draw_matrix(self.matrix, self.listsubimage)

    def get_best(self, matrix):
        new_matrix = matrix
        ver, hor = new_matrix.shape
        ver_half, hor_half = int(ver/2), int(hor/2)
        print(ver_half, hor_half)
        for i in range(1, ver_half):
            for j in range(1, hor_half):
                
                prev_idx = new_matrix[i][j-1]
                up_idx = new_matrix[i-1][j]

                if prev_idx is None or up_idx is None:
                    continue

                prev_piece = self.listsubimage[prev_idx]
                up_piece = self.listsubimage[up_idx]

                result_arr, is_single = self.get_common_two_arr3(new_matrix, prev_piece, up_piece, 1, 2)
                # print(i, j, len(result_arr))
                if len(result_arr) >= 1:
                    new_matrix[i][j] = result_arr[0][1]
                    # utilities.draw_matrix(new_matrix, self.listsubimage)

        for i in range(1, ver_half):
            for j in reversed(range(hor_half + 1, hor - 1)):
                next_idx = new_matrix[i][j+1]
                up_idx = new_matrix[i-1][j]

                if next_idx is None or up_idx is None:
                    continue
                next_piece = self.listsubimage[next_idx]
                up_piece = self.listsubimage[up_idx]

                result_arr, is_single = self.get_common_two_arr3(new_matrix, next_piece, up_piece, 3, 2)
                # print(i, j, len(result_arr))
                if len(result_arr) >= 1:
                    new_matrix[i][j] = result_arr[0][1]
                    # utilities.draw_matrix(new_matrix, self.listsubimage)

        for i in reversed(range(ver_half + 1, ver - 1)):
            for j in (range(1, hor_half)):
                down_idx = new_matrix[i+1][j]
                prev_idx = new_matrix[i][j-1]

                if down_idx is None or prev_idx is None:
                    continue
                down_piece = self.listsubimage[down_idx]
                prev_piece = self.listsubimage[prev_idx]

                result_arr, is_single = self.get_common_two_arr3(new_matrix, down_piece, prev_piece, 0, 1)
                # print(i, j, len(result_arr))
                if len(result_arr) >= 1:
                    new_matrix[i][j] = result_arr[0][1]
                    # utilities.draw_matrix(new_matrix, self.listsubimage)

        for i in reversed(range(ver_half + 1, ver - 1)):
            for j in reversed(range(hor_half + 1, hor - 1)):
                down_idx = new_matrix[i+1][j]
                next_idx = new_matrix[i][j+1]

                if down_idx is None or next_idx is None:
                    continue
                down_piece = self.listsubimage[down_idx]
                next_piece = self.listsubimage[next_idx]

                result_arr, is_single = self.get_common_two_arr3(new_matrix, down_piece, next_piece, 0, 3)
                # print(i, j, len(result_arr))
                if len(result_arr) >= 1:
                    new_matrix[i][j] = result_arr[0][1]
                    # utilities.draw_matrix(new_matrix, self.listsubimage)

        print(new_matrix)  

    def get_min_distance_matrix(self, arr_ver, matrix, position):
        ver, hor = matrix.shape
        arr2 = [[idx for diff, idx in item] for item in arr_ver]
        result = list(itertools.product(*arr2))
        result = [item  for item in result if len(list(set(item))) == len(item)]

        arr_new_matrix = []
        for item in result:
            new_matrix = matrix.copy()
            for i in range(1, ver - 1):
                new_matrix[i][position] = item[i-1]
            arr_new_matrix.append(new_matrix)

        arr = [ Pieces(self.listsubimage, new_matrix) for new_matrix in arr_new_matrix]
        arr = sorted(arr, key=lambda x: x.total_distance)
        return arr

    def check_in_matrix(self, matrix, idx):
        temp = matrix.flatten()
        return idx not in temp

    def abc(self, matrix):
        ver, hor = matrix.shape
        for i in range(1, hor - 1):
            arr_ver  = [[] for i in range(1, ver - 1)]
            for j in range(1, ver - 1):
                prev_idx =  matrix[j][i-1]
                prev_piece = self.listsubimage[prev_idx]
                prev_right = prev_piece.difference_side[1]
                # if(prev_right[1][0] -  prev_right[0][0] < 50):
                arr_right = [ (diff, idx) for diff, idx in prev_right if diff < 60 and self.check_in_matrix(matrix, idx)]
                # arr_ver[j-1].append(prev_right[1])
                # arr_ver[j-1].append(prev_right[0])
                arr_ver[j - 1] = arr_right
            
            arr = self.get_min_distance_matrix(arr_ver, matrix, i)
            
            utilities.draw_matrix(arr[0].matrix, self.listsubimage)
            break
            bac = ""

    def get_common_two_arr2(self, matrix, prev_piece, up_piece, index1, index2, right_of_current_piece):
        ver, hor = matrix.shape
        prev_right = prev_piece.difference_side[index1]
        up_down = up_piece.difference_side[index2]

        flat_matrix = matrix.flatten()
        prev_right = [ (diff, idx) for diff, idx in prev_right if idx not in flat_matrix]
        up_down = [(diff, idx) for diff, idx in up_down if idx not in flat_matrix]

        prev_right_copy = prev_right.copy()
        up_down_copy = up_down.copy()

        combine = prev_right + up_down
        combine = [item[1] for item in combine]
        combine = list(set(combine))
        combine_arr = []

        for idx in combine:
            prev_diff, up_diff = prev_piece.difference[idx].copy(), up_piece.difference[idx].copy()
            prev_diff = sorted(prev_diff, key=lambda x: x[1])
            up_diff =  sorted(up_diff, key=lambda x: x[1])
            diff_prev, direc_prev = prev_diff[index1]
            diff_up, direc_up = up_diff[index2]

            right_diff = right_of_current_piece.difference[idx]
            if  right_diff is not None: 
                right_diff = right_diff.copy()
                right_diff = sorted(right_diff, key=lambda x: x[1])
                diff_down, direc_down = right_diff[3]
                combine_arr.append(((diff_prev + diff_up  + diff_down), idx))
            else:
                combine_arr.append(((diff_prev + diff_up), idx))


        # for i in range(len(prev_right)):
        #     diff_new_prev, idx_new_prev = prev_right[i]
        #     new_piece = self.listsubimage[idx_new_prev]
        #     for diff_down, idx_down in up_down:
        #         piece_up = self.listsubimage[idx_down]
        #         diff, direc = piece_up.difference[idx_new_prev][0]
        #         combine.append((diff + diff_new_prev), idx_new_prev)
        combine_arr = sorted(combine_arr, key=lambda x: x[0])
        combine_arr = utilities.get_only_max_value(combine_arr)
        return combine_arr, True


    def get_common_two_arr(self, prev_right, up_down, matrix, right_left=None):
        prev_diff_min = prev_right[0][0]
        up_diff_min = up_down[0][0]

        prev_right = [ (diff, idx) for diff, idx in prev_right if diff == prev_diff_min]
        up_down = [(diff, idx) for diff, idx in up_down if diff == up_diff_min]

        flat_matrix = matrix.flatten()
        prev_right = [ (diff, idx) for diff, idx in prev_right if idx not in flat_matrix]
        up_down = [(diff, idx) for diff, idx in up_down if idx not in flat_matrix]

        prev_right_copy = prev_right.copy()
        up_down_copy = up_down.copy()

        prev_right_idx = [idx for diff, idx in prev_right]
        prev_right_diff = np.asarray([idx for diff, idx in prev_right])

        up_down_idx = [idx for diff, idx in up_down]
        up_down_diff = np.asarray([idx for diff, idx in up_down])

        result_idx = list(set(prev_right_idx).intersection(set(up_down_idx)))

        # if  right_left is not None:
        #     right_left = [(diff, idx) for diff, idx in right_left if diff == right_left[0][1]]

        #     right_left_idx = [idx for diff, idx in right_left]
        #     right_left_diff = np.asarray([idx for diff, idx in right_left])

        #     result_idx = list(set(prev_right_idx).intersection(set(up_down_idx).intersection(set(right_left_diff))))
        
        prev_right = [ (diff, idx) for diff, idx in prev_right if idx in result_idx ]
        up_down = [ (diff, idx) for diff, idx in up_down if idx in result_idx ]
        # if  right_left is not None:
        #     right_left = [ (diff, idx) for diff, idx in right_left if idx in result_idx ]

        result_arr = []
        for i in range(len(result_idx)):
            id = result_idx[i]
            
            prev_diff, prev_idx =  [ (diff, idx) for diff, idx in prev_right if idx == id ][0]
            up_diff, up_idx =  [ (diff, idx) for diff, idx in up_down if idx == id ][0]

            result_arr.append((prev_diff + up_diff, prev_idx))

        if(len(result_arr) != 0):
            return result_arr, len(result_arr) == 1
        else:
            result_arr = prev_right_copy + up_down_copy
            result_arr = sorted(result_arr, key=lambda x: x[0])
            return result_arr[:1], False

    # def create_sub_array(self):
    #     for i in range(1, self.vertical - 1):
    #         for j in  range(1, self.horizontal - 1):
    #             idx = self.matrix[i][j]
    #             if(idx is not None): continue
    #             prev_idx = self.matrix[i][j-1]
    #             print(prev_idx)
    #             up_idx = self.matrix[i-1][j]
    #             right_idx = self.matrix[i][j+1]

    #             right_left = None
    #             if(j == self.horizontal - 2): right_left = self.listsubimage[right_idx].difference_side[3]
    #             prev_piece = self.listsubimage[prev_idx]
    #             up_piece = self.listsubimage[up_idx]

    #             prev_right = prev_piece.difference_side[1]
    #             up_down = up_piece.difference_side[2]

    #             result_arr, is_single = self.get_common_two_arr(prev_right, up_down, right_left)
    #             self.matrix[i][j] = result_arr[0][0]

    def get_common_two_arr3(self, matrix, prev_piece, up_piece, idx1, idx2):
        flat_matrix = matrix.flatten()
        prev_right = prev_piece.difference_side[idx1]
        up_down = up_piece.difference_side[idx2]

        prev_right = [ (diff, idx) for diff, idx in prev_right if idx not in flat_matrix]
        up_down = [(diff, idx) for diff, idx in up_down if idx not in flat_matrix]

        prev_right_copy = prev_right.copy()

        combine = prev_right
        combine = [item[1] for item in combine]
        combine = list(set(combine))
        combine_arr = []

        for idx in combine:
            prev_diff, up_diff = prev_piece.difference[idx].copy(), up_piece.difference[idx].copy()
            prev_diff = sorted(prev_diff, key=lambda x: x[1])
            up_diff =  sorted(up_diff, key=lambda x: x[1])
            diff_prev, direc_prev = prev_diff[idx1]
            diff_up, direc_up = up_diff[idx2]

            combine_arr.append(((diff_prev + diff_up), idx))

        

        combine_arr = sorted(combine_arr, key=lambda x: x[0])

        abc = ""
        # combine_arr = [(diff, idx) for diff, idx in combine_arr if  diff < 100]
        # combine_arr = utilities.get_only_max_value(combine_arr)
        return combine_arr, True

    def create_sub_array(self, matrix):
        current_matrix = matrix
        if(utilities.check_matrix_full(current_matrix)):
            return current_matrix

        while utilities.get_remain_matrix(current_matrix) != 0:
            i, j = utilities.get_next_point(matrix, False)
            prev_idx = current_matrix[i][j-1]
            next_idx = current_matrix[i][j+1]
            up_idx = current_matrix[i-1][j]
            down_idx = current_matrix[i+1][j]
            
            right_of_current_idx = current_matrix[i][j+1]

            # right_of_current_piece = None
            # if right_of_current_idx is  None:
            #     up_next_idx = current_matrix[i-1][j+1]
            #     up_next_piece = self.listsubimage[up_next_idx]
            #     diff, right_of_current_idx =  up_next_piece.difference_side[2][0]
            # right_of_current_piece  = self.listsubimage[right_of_current_idx]

            # prev_piece.difference_side[index1]
            
            result_arr, is_single = [], False
            prev_piece = self.listsubimage[prev_idx]
            up_piece = self.listsubimage[up_idx]
            # result_arr, is_single = self.get_common_two_arr2(current_matrix, prev_piece, up_piece, 1, 2, right_of_current_piece)



            # if(direction == 0):
            #     prev_piece = self.listsubimage[prev_idx]
            #     up_piece = self.listsubimage[up_idx]
            #     result_arr, is_single = self.get_common_two_arr2(current_matrix, prev_piece, up_piece, 1, 2)
            # elif(direction == 1):
            #     up_piece = self.listsubimage[up_idx]
            #     next_piece = self.listsubimage[next_idx]
            #     result_arr, is_single = self.get_common_two_arr2(current_matrix, up_piece, next_piece, 2, 3)
            # elif(direction == 2):
            #     prev_piece = self.listsubimage[prev_idx]
            #     down_piece = self.listsubimage[down_idx]
            #     result_arr, is_single = self.get_common_two_arr2(current_matrix, prev_piece, down_piece, 1, 0)
            # elif(direction == 3):
            #     next_piece = self.listsubimage[next_idx]
            #     down_piece = self.listsubimage[down_idx]
            #     result_arr, is_single = self.get_common_two_arr2(current_matrix, down_piece, next_piece, 0, 3)

            result_arr, is_single = self.get_common_two_arr3(current_matrix, prev_piece, up_piece)
            # print(prev_piece.piecenum, up_piece.piecenum, result_arr)
            # print(result_arr)
            if is_single:
                current_matrix[i][j] = result_arr[0][1]
                # utilities.draw_matrix(current_matrix, self.listsubimage)
                abc = ""
            else:
                for diff, idx  in result_arr:
                    new_matrix = current_matrix.copy()
                    new_matrix[i][j] = idx
                    # utilities.draw_matrix(new_matrix, self.listsubimage)
                    result = self.create_sub_array(new_matrix)
                    if result is not None:
                        self.append_list_matrix(result)
                break
        if matrix is not None and utilities.get_remain_matrix(current_matrix) == 0:
            self.append_list_matrix(matrix)
            

    def find_neighbors(self, origin_list_piece, head_point, end_point, matrix_orented_func, piece_except=[]):
        debug = (head_point == 67 and end_point == 58)
        
        temp_list_piece = [piece.piecenum for piece in  origin_list_piece if piece.piecenum not in piece_except]
        new_list_piece = list(permutations(temp_list_piece))
        new_list_piece = [ (head_point,)  + piece  + (end_point,) for piece in new_list_piece]
        arr = [ Pieces(self.listsubimage, matrix_orented_func(piece), debug) for piece in new_list_piece]
        arr = sorted(arr, key=lambda x: x.total_distance)
        return arr[0]

    def create_matrix_hor_up(self, list_piece):
        matrix = np.asarray([  [None for j in range(self.horizontal)] for i in range(self.vertical)])
        # print(matrix)
        i, j = -1, 0
        for idx in range(len(list_piece)):
            if(idx %  (self.horizontal)  == 0):
                i+=1
                j = 0
            else:
                j += 1
            matrix[i][j] = list_piece[idx]
        return matrix

    def create_matrix_hor_down(self, list_piece):
        matrix = np.asarray([  [None for j in range(self.horizontal)] for i in range(self.vertical)])
        # print(matrix)
        i, j = 0, 0
        for idx in range(len(list_piece)):
            matrix[-1][j] = list_piece[idx]
            j += 1
        return matrix

    def create_matrix_ver_left(self, list_piece):
        matrix = np.asarray([  [None for j in range(self.horizontal)] for i in range(self.vertical)])
        i, j = 0, 0
        for idx in range(len(list_piece)):
            matrix[i][j] = list_piece[idx]
            i += 1
        return matrix

    def create_matrix_ver_right(self, list_piece):
        matrix = np.asarray([  [None for j in range(self.horizontal)] for i in range(self.vertical)])
        i, j = 0, -1
        for idx in range(len(list_piece)):
            matrix[i][j] = list_piece[idx]
            i += 1
        return matrix
