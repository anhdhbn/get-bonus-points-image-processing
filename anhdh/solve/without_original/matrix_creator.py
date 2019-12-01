import numpy as np

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
