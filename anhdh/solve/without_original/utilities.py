from PIL import Image
import numpy as np
import os
import json
from skimage import color

from anhdh.solve.without_original.Piece import Piece
from anhdh.solve.TypeEdge import *





def read_data_to_obj(folder_process, path):
    with open(os.path.join(folder_process, path)) as f:
        data = f.read()
    return json.loads(data)

def get_arr_except(maxtrix):
    matrix_flatten = maxtrix.flatten()
    arr_except = [obj for obj in matrix_flatten if obj is not None ]
    return arr_except

def get_arr_sub(maxtrix, listsubimage):
    """
    get array except border
    """
    arr_except = get_arr_except(maxtrix)
    

    result = [item for item in listsubimage if item.piecenum  not in arr_except]
    print([item.piecenum for item in result])
    return result

def get_remain_matrix(matrix):
    ver, hor = matrix.shape
    temp = np.array([[None for j in range(hor)]  for i in range(ver)])
    checker = (matrix == temp).sum()
    return checker

def check_matrix_full(matrix):
    return get_remain_matrix(matrix) == 0

def get_next_point(matrix, four_cor=True):
    ver, hor = matrix.shape
    ver_half, hor_half = int(ver/2), int(hor/2)
    for i in range(1, ver-1):
        for j in range(1, hor-1):
            if four_cor:
                if j  <= hor_half:
                    if i <= ver_half:
                        if matrix[i][j] is None:
                            return i, j, 0
                    else:
                        new_i = (ver-1)-(ver_half-i)
                        if matrix[new_i][j] is None:
                            return i, j, 1
                else:
                    if i <= ver_half:
                        new_j = (hor-1)-(hor_half-i)
                        if matrix[i][new_j] is None:
                            return i, j, 2
                    else:
                        new_j = (hor-1)-(hor_half-i)
                        new_i = (ver-1)-(ver_half-i)
                        if matrix[new_i][new_j] is None:
                            return i, j, 3
            else:
                if matrix[i][j] is None:
                    return i, j
            
    return None

def get_only_max_value(arr):
    temp = arr[0]
    return [item for item in arr if item == temp]


            
def luminance(pixel):
    return (0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2])

def is_similar(pixel_a, pixel_b, threshold=30):
    return abs(luminance(pixel_a) - luminance(pixel_b)) < threshold

def pixel_difference(px1, px2, debug=False):
    PIXEL_DIFFERENCE_THRESHOLD = 20
    diff = 0
    for i in range(len(px1)):
        diff += abs(int(px1[i] - int(px2[i])))
    # print(diff)
    return False if diff < PIXEL_DIFFERENCE_THRESHOLD else True

def side_difference(side1, side2, debug=False):
    difference = 0
    for i in range(len(side1)):
        difference += 1 if pixel_difference(side1[i], side2[i], debug) else 0
    return difference

def get_lab_colors(edge):
    lab_colors = []
    for r, g, b in edge:
        lab_colors.append(color.rgb2lab([[[r / 255.0, g / 255.0, b / 255.0]]])[0][0])
        lab_colors[-1] = [0, lab_colors[-1][1], lab_colors[-1][2]]
    return lab_colors

def euclideanDistance(e1_lab_colors, e2_lab_colors):
    # print(np.asarray(e1_lab_colors).shape, np.asarray(e2_lab_colors).shape)
    sum = 0
    max = 50
    len1 = len(e1_lab_colors)
    len2 = len(e2_lab_colors)
    if len1 < len2:
        max = len1
    else:
        max = len2
    t1 = len1 / max
    t2 = len2 / max

    def dist_color(tuple1, tuple2):
        return np.sqrt((tuple1[0] - tuple2[0]) ** 2
                        + (tuple1[1] - tuple2[1]) ** 2
                        + (tuple1[2] - tuple2[2]) ** 2)

    for i in range(max):
        sum += dist_color(e1_lab_colors[int(t1 * i)], e2_lab_colors[int(t2 * i)])
    return sum

def side_difference_lab(side1, side2):
    e1 = get_lab_colors(side1)
    e2 = get_lab_colors(side2)

    len1 = len(e1)
    len2 = len(e2)
    if len1 < len2:
        max_ = len1
    else:
        max_ = len2

    new_e1 = e1[:max_]
    new_e2 = e2[:max_]

    # val = min(euclideanDistance(e1, e2), euclideanDistance(e1, e2[::-1]))
    val = np.linalg.norm(np.asarray(new_e1)-np.asarray(new_e2))
    return val

def side_difference_surf(edge1, edge2, use_rgb=True, debug=False):
    side_diff = side_difference
    if not use_rgb: side_diff = side_difference_lab
    side1 = edge1.color_edge
    side2 = edge2.color_edge

    if((edge1.typeEdge == TypeEdge.HUMP or edge1.typeEdge == TypeEdge.REVERSE_HUMP) and edge2.typeEdge == TypeEdge.BORDER) or (edge1.typeEdge == TypeEdge.BORDER and (edge2.typeEdge == TypeEdge.REVERSE_HUMP or edge2.typeEdge == TypeEdge.HUMP)):
        return 1000000

    if len(side1)  == len(side2):
        return side_diff(side1, side2, debug)
        # return side_difference_lab(side1, side2)
    elif(len(side1)  >  len(side2)):
        longer, shorter = side1, side2
    else:
        longer, shorter = side2, side1
    more =  len(longer)  - len(shorter)
    arr_diff = []
    for i in range(0, more):
        newlonger = longer[i+1:]
        still_more  =  len(newlonger) - len(shorter)
        newlonger = newlonger[:len(newlonger)-still_more]
        arr_diff.append(side_diff(newlonger, shorter))
        # arr_diff.append(side_difference_lab(newlonger, shorter))
    arr_diff = sorted(arr_diff)
    return arr_diff[0]

def piece_difference(piece1: Piece, piece2: Piece, use_rgb=True): 

    vertical_12 = side_difference_surf(piece1.edgeDown, piece2.edgeUp, use_rgb)
    vertical_21 = side_difference_surf(piece2.edgeDown, piece1.edgeUp, use_rgb)
    horizontal_12 = side_difference_surf(piece1.edgeRight, piece2.edgeLeft, use_rgb)
    horizontal_21 = side_difference_surf(piece2.edgeRight, piece1.edgeLeft, use_rgb)

    # clockwise direction
    temp1 = [vertical_21, horizontal_12, vertical_12, horizontal_21]
    temp2 = [vertical_12, horizontal_21, vertical_21, horizontal_12]

    for i in range(len(temp1)):
        temp1[i] = (temp1[i], i)
        temp2[i] = (temp2[i], i)

    if use_rgb:
        piece1.difference[piece2.piecenum] = sorted(temp1)
        piece2.difference[piece1.piecenum] = sorted(temp2)
    else:
        piece1.difference2[piece2.piecenum] = sorted(temp1)
        piece2.difference2[piece1.piecenum] = sorted(temp2)


