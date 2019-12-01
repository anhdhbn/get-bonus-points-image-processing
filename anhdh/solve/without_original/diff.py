from anhdh.solve.original.Piece import Piece
from anhdh.solve.TypeEdge import TypeEdge, Direction
import numpy as np


class Diff(object):

    def side_difference(self, side1, side2):
        raise NotImplementedError

    def side_difference_surf(self, edge1, edge2):
        side1 = edge1.color_edge
        side2 = edge2.color_edge

        if((edge1.typeEdge == TypeEdge.HUMP or edge1.typeEdge == TypeEdge.REVERSE_HUMP) and edge2.typeEdge == TypeEdge.BORDER) or (edge1.typeEdge == TypeEdge.BORDER and (edge2.typeEdge == TypeEdge.REVERSE_HUMP or edge2.typeEdge == TypeEdge.HUMP)):
            return 1000000

        if len(side1)  == len(side2):
            return self.side_difference(side1, side2)
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
            arr_diff.append(self.side_difference(newlonger, shorter))
        arr_diff = sorted(arr_diff)
        return arr_diff[0]
        
    def piece_difference(self, piece1: Piece, piece2: Piece): 
        vertical_12 = self.side_difference_surf(piece1.edge[2], piece2.edge[0])
        vertical_21 = self.side_difference_surf(piece2.edge[2], piece1.edge[0])
        horizontal_12 = self.side_difference_surf(piece1.edge[1], piece2.edge[3])
        horizontal_21 = self.side_difference_surf(piece2.edge[1], piece1.edge[3])

        # clockwise direction
        temp1 = [vertical_21, horizontal_12, vertical_12, horizontal_21]
        temp2 = [vertical_12, horizontal_21, vertical_21, horizontal_12]

        for i in range(len(temp1)):
            temp1[i] = (temp1[i], i)
            temp2[i] = (temp2[i], i)

        piece1.difference[piece2.piecenum] = sorted(temp1)
        piece2.difference[piece1.piecenum] = sorted(temp2)

class DiffRGB(Diff):
    def __init__(self):
        self.PIXEL_DIFFERENCE_THRESHOLD = 10

    def side_difference(self, side1, side2):
        difference = 0
        for i in range(len(side1)):
            difference += 1 if self.pixel_difference(side1[i], side2[i]) else 0
        return difference

    def pixel_difference(self, px1, px2, debug=False):
        diff = 0
        for i in range(len(px1)):
            diff += abs(int(px1[i] - int(px2[i])))
        return False if diff < self.PIXEL_DIFFERENCE_THRESHOLD else True

class DiffLab(Diff):

    def side_difference(self, side1, side2):
        e1 = self.get_lab_colors(side1)
        e2 = self.get_lab_colors(side2)

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
    

    def get_lab_colors(self, edge):
        from skimage import color
        lab_colors = []
        for r, g, b in edge:
            lab_colors.append(color.rgb2lab([[[r / 255.0, g / 255.0, b / 255.0]]])[0][0])
            lab_colors[-1] = [0, lab_colors[-1][1], lab_colors[-1][2]]
        return lab_colors

    def euclideanDistance(self, e1_lab_colors, e2_lab_colors):
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
