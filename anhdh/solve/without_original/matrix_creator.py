import numpy as np
import itertools
from anhdh.solve.without_original.Pieces import Pieces

from itertools import permutations

def create_matrix_hor_up(list_piece, horizontal, vertical):
    matrix = np.asarray([  [None for j in range(horizontal)] for i in range(vertical)])
    # print(matrix)
    i, j = -1, 0
    for idx in range(len(list_piece)):
        if(idx %  (horizontal)  == 0):
            i+=1
            j = 0
        else:
            j += 1
        matrix[i][j] = list_piece[idx]
    return matrix

def create_matrix_hor_down(list_piece, horizontal, vertical):
    matrix = np.asarray([  [None for j in range(horizontal)] for i in range(vertical)])
    # print(matrix)
    i, j = 0, 0
    for idx in range(len(list_piece)):
        matrix[-1][j] = list_piece[idx]
        j += 1
    return matrix

def create_matrix_ver_left(list_piece, horizontal, vertical):
    matrix = np.asarray([  [None for j in range(horizontal)] for i in range(vertical)])
    i, j = 0, 0
    for idx in range(len(list_piece)):
        matrix[i][j] = list_piece[idx]
        i += 1
    return matrix

def create_matrix_ver_right(list_piece, horizontal, vertical):
    matrix = np.asarray([  [None for j in range(horizontal)] for i in range(vertical)])
    i, j = 0, -1
    for idx in range(len(list_piece)):
        matrix[i][j] = list_piece[idx]
        i += 1
    return matrix

def get_min_distance_matrix(arr_ver, matrix, position, listsubimage):
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

    arr = [ Pieces(listsubimage, new_matrix) for new_matrix in arr_new_matrix]
    arr = sorted(arr, key=lambda x: x.total_distance)
    return arr

def brute_force(arr_remain, matrix, listsubimage):
    import  time
    start = time.time()
    new_list_piece = list(permutations(arr_remain))
    print(time.time() - start)
    return []