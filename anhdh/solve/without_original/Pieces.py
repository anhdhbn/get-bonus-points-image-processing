from anhdh.solve.without_original.Piece import Piece
from anhdh.solve.TypeEdge import *

class Pieces(object):
    def __init__(self, original_list_piece, ordered_piece_matrix, debug  = False):
        self.list_piece = original_list_piece.copy()
        self.total_distance = 0
        self.matrix = ordered_piece_matrix
        self.init_distance(debug)

    def init_distance(self, debug):
        vertical, horizontal = self.matrix.shape
        caculated = []
        for i in range(vertical):
            for j in range(horizontal):
                piecenum = self.matrix[i][j]
                if piecenum is None: continue

                idx_down, idx_right = None, None
                if i != vertical - 1:
                    idx_down = self.matrix[i+1][j]

                if j != horizontal -1:
                    idx_right = self.matrix[i][j+1]

                current_piece = self.list_piece[piecenum]

                if idx_right is not None and idx_right not in caculated:
                    caculated.append(idx_right)
                    diff = current_piece.difference[idx_right]
                    if diff is not None:
                        dis, direc = [(dis, direc) for dis, direc  in diff if direc == 1][0]
                        self.total_distance += dis if dis < 1000  else 0

                if idx_down is not None and idx_right not in caculated:
                    caculated.append(idx_down)
                    diff = current_piece.difference[idx_down]
                    if diff is not None:
                        dis, direc = [(dis, direc) for dis, direc  in diff if direc == 2][0]
                        self.total_distance += dis if dis < 1000  else 0





    # def find_neighbors(self, piece_except = [], full_search=False):
    #     candidates = [None for x in range(4)]
    #     # find the best candidate for each direction
    #     for i in range(len(self.difference)):
    #         if i in piece_except:
    #             continue
    #         if self.difference[i] is None:
    #             continue
    #         if full_search:
    #             for temp in  self.difference[i]:
    #             # temp = self.difference[i][0] # lay cai max
    #                 if temp[0] == 1000000: continue
    #                 direction = temp[1]
    #                 if candidates[direction] is None or candidates[direction][1][0] > temp[0]:
    #                     candidates[direction] = (i, temp)
    #         else:
    #             temp = self.difference[i][0] # lay cai max
    #             if temp[0] == 1000000: continue
    #             direction = temp[1]
    #             if candidates[direction] is None or candidates[direction][1][0] > temp[0]:
    #                 candidates[direction] = (i, temp)

    #     for i in range(4):
    #         if self.edges[i].typeEdge == TypeEdge.BORDER:
    #             candidates[i] = None
    #     for entry in candidates:
    #         if entry is not None:
    #             self.neighbors[entry[1][1]] = entry[0]
    #             # if entry[1][0] <= self.DIFFERENCE_RATE_THRESHOLD * max(self.width, self.height):
    #                 # self.neighbors[entry[1][1]] = entry[0]
        