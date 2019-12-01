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
from anhdh.solve.TypeEdge import TypeEdge 

class Solver(Common):
    def __init__(self, img_path):
        Common.__init__(self, img_path)
        self.listsubimg_path = glob.glob(f"{self.raster_folder}/*.png")
        self.image = cv2.imread(img_path)
        self.listsubimage = [cv2.imread(path) for path in self.listsubimg_path]
        self.init_sub_img()
        self.init_size()
        self.matrix = np.zeros((self.num_vertical, self.num_horizontal), dtype=int)
    
    def init_size(self):
        self.num_horizontal = len([item for item in self.listsubimage if item.check_type(0, TypeEdge.BORDER)]) + 2
        self.num_vertical  = len([item for item in self.listsubimage if item.check_type(3, TypeEdge.BORDER)]) + 2
    
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
        self.listsubimg_path  = sorted(self.listsubimg_path, key=lambda x: utilities.get_id_by_path(x))
        self.listsubimage = []
        for idx, path in enumerate(self.listsubimg_path):
            name = os.path.basename(path)
            name = name.replace(".png", "")
            name = name.split("-")[2]
            temp = pieces_obj[name]
            piece = Piece(path, idx, len(self.listsubimg_path), utilities.crop_img(self.folder_process, temp[1], temp[0]))
            self.listsubimage.append(piece)