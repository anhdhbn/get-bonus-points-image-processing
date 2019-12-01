#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pixsaw.base import Handler
from pathlib import Path
import os
import cairosvg

from anhdh.Common import Common

class Cutter(Common):
    def __init__(self, img_path):
        Common.__init__(self, img_path)

    def convert_svg_to_png(self):
        cairosvg.svg2png(url=os.path.join(self.folder, f"{self.name}_mask.svg"), write_to=os.path.join(self.folder, f"{self.name}_mask.png"))
        cairosvg.svg2png(url=os.path.join(self.folder, f"{self.name}.svg"), write_to=os.path.join(self.folder, f"{self.name}.png"))

    def process(self):
        self.convert_svg_to_png()
        self.linesfile = os.path.join(self.folder, f"{self.name}_mask.png")
        self.handler = Handler(self.folder_process, self.linesfile,raster_dir='raster', jpg_dir='jpg')
        self.handler.process(self.img_path)