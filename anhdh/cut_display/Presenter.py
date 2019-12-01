#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image
import os
import glob
import json
from random import randint, shuffle

from collections import OrderedDict

from anhdh.Common import Common


class Presenter(Common):
    def __init__(self, img_path):
        Common.__init__(self, img_path)
        self.image = Image.open(img_path).convert('RGBA')
        self.width, self.height = self.image.size
        self.imagecutpath = Image.open(os.path.join(self.folder, f"{self.name}.png")).convert('RGBA')
        self.imagecutrandom = Image.new('RGBA', (self.width*2, self.height*2), (255, 255, 255, 255))
        self.listsubimg_path = glob.glob(f"{self.raster_folder}/*.png")
        self.listsubimg = [ Image.open(path) for path in self.listsubimg_path]
        self.pieces = {}
        self.pieces_copy = None

    def get_rand(self, maxnum):
        return randint(0, maxnum)
    
    def get_rand_piece(self):
        data = self.pieces_copy.pop()
        return data

    def Display(self):
        self.image.show()
        self.imagecutpath.show()
        with open(f"{self.folder_process}/pieces.json") as f:
            data_pieces = f.read()
        self.pieces = json.loads(data_pieces)
        self.pieces_copy = self.pieces
        self.pieces_copy = list(self.pieces_copy.items())
        shuffle(self.pieces_copy)

        for i in range(len(self.pieces)):
            _, (a, b, c, d) = self.get_rand_piece()
            self.imagecutrandom.paste(self.listsubimg[i], (a*2, b*2))
        
        for i in range(self.width*2):
            for j in range(self.height*2):
                color = self.imagecutrandom.getpixel((i,j))
                
                if color == (0, 0, 0, 0):
                    self.imagecutrandom.putpixel((i, j), (255, 255,  255, 255))
        
        border = Image.new('RGBA', (self.width*2+10, self.height*2+10), (255, 255,  255, 255))
        border.paste(self.imagecutrandom, (10, 10))
        self.imagecutrandom = border
        self.imagecutrandom.show()
        self.imagecutrandom.save(os.path.join(self.folder, f"{self.name}_random.png"))
