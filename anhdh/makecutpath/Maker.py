#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PIL import Image
import math
import random
from pathlib import Path
import os
import shutil

from anhdh.makecutpath.Vector import Vector
from anhdh.makecutpath import utilities
from anhdh.Common import  Common

class Maker(Common):
    def __init__(self, img_path, make_random=False, min_pixel=100):
        Common.__init__(self, img_path)
        self.make_random = make_random
        self.min_pixel  = min_pixel
        self.image = Image.open(img_path).convert('RGBA')
        self.width, self.height = self.image.size
        self.number_row = math.ceil(self.height/self.min_pixel)
        self.number_column = math.ceil(self.width/self.min_pixel)
        self.corner_radius = self.min_pixel/2     
    
    def write_header(self):
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        shutil.copy(self.img_path, os.path.join(self.output, self.basename))
        self.filewriter = open(os.path.join(self.folder, f"{self.name}.svg"), "w")
        self.maskwriter = open(os.path.join(self.folder, f"{self.name}_mask.svg"), "w")

        utilities.write_header(self.filewriter, self.width, self.height, self.img_path)
        utilities.write_header(self.maskwriter, self.width, self.height)
        
    
    def write_polyline(self, p, color):
        utilities.write_polyline(self.filewriter, p, color)
        utilities.write_polyline(self.maskwriter, p, color)

    def write_footer(self):
        utilities.write_footer(self.filewriter)
        utilities.write_footer(self.maskwriter)
    
    def close_all_file(self):
        self.filewriter.close()
        self.maskwriter.close()

    def make_cut_path(self):
        self.write_header()

        # Horizontal lines.
        # column = 0
        # row = 0
        # start = Vector(column*WIDTH/COLUMN_COUNT, (row + 1)*HEIGHT/ROW_COUNT)
        # end = Vector((column + 1)*WIDTH/COLUMN_COUNT, (row + 1)*HEIGHT/ROW_COUNT)
        # print(start, end)
        for row in range(self.number_row - 1):
            for column in range(self.number_column):
                start = Vector(column*self.width/self.number_column, (row + 1)*self.height/self.number_row)
                end = Vector((column + 1)*self.width/self.number_column, (row + 1)*self.height/self.number_row)
                self.make_knob(start, end, "#000000")
                # print(start, end)

        # Vertical lines.
        for row in range(self.number_row):
            for column in range(self.number_column - 1):
                start = Vector((column + 1)*self.width/self.number_column, row*self.height/self.number_row)
                end = Vector((column + 1)*self.width/self.number_column, (row + 1)*self.height/self.number_row)
                self.make_knob(start, end, "#000000")

        self.write_footer()
        self.close_all_file()
        
    
    def append_circle(self, p, v, n, center, radius, start_angle, end_angle):
        """Append a circle to list of Vector points "p". The orthonormal "v" and
        "n" vectors represent the basis vectors for the circle. The "center"
        vector is the circle's center, and the start and end angle are relative
        to the basis vectors. An angle of 0 means all "v", tau/4 means all "n"."""

        # Fraction of the circle we're covering, in radians.
        angle_span = end_angle - start_angle

        # The number of segments we want to use for this span. Use 20 for a full circle.
        segment_count = int(math.ceil(20*math.fabs(angle_span)/(2*math.pi)))

        for i in range(segment_count + 1):
            th = start_angle + angle_span*i/segment_count
            point = center + v*math.cos(th)*radius + n*math.sin(th)*radius
            p.append(point)

    def make_knob(self, start, end, color):
        """Make a knob (the part that sticks out from one piece into another).
        This includes the entire segment on the side of a square.  "start" and
        "end" are points that represent the ends of the line segment. In other
        words, if we have a puzzle piece with four corners, then call this
        function four times with the four corners in succession."""

        # Length of the line on the side of the puzzle piece.

        # Choose the base of the knob. Pick the midpoint of the line
        # and purturb it a bit.
        if self.make_random: mid = start + (end - start)*(0.4 + random.random()*0.2)
        else: mid = start + (end - start)*(0.5)

        # The first part of our basis vector. This points down the edge.
        v = (end - start).normalized()

        # Pick a random direction for the knob (1 or -1).
        # direction = random.randint(0, 1)*2 - 1
        if self.make_random: direction = random.randint(0, 1)*2 - 1
        else: direction = -1

        # Find the other axis, normal to the line.
        n = v.reciprocal()*direction

        # Where the knob starts and ends, along the line.
        knob_start = mid - v*self.min_pixel*0.1
        knob_end = mid + v*self.min_pixel*0.1

        # Radius of the small circle that comes off the edge.
        # small_radius = line_length*(0.05 + random.random()*0.01)
        if self.make_random: small_radius = self.min_pixel*(0.06 + random.random()*0.01)
        else: small_radius = self.min_pixel*(0.06)

        # Radius of the larger circle that makes the actual knob.
        large_radius = small_radius*1.3

        # Magic happens here. See this page for an explanation:
        # http://www.teamten.com/lawrence/projects/jigsaw-puzzle-on-laser-cutter/
        tri_base = (knob_end - knob_start).length()/2
        tri_hyp = small_radius + large_radius
        tri_height = math.sqrt(tri_hyp**2 - tri_base**2)
        large_center_distance = small_radius + tri_height
        small_start_angle = -(2*math.pi)/4
        small_end_angle = math.asin(tri_height/tri_hyp)
        large_slice_angle = math.asin(tri_base/tri_hyp)
        large_start_angle = (2*math.pi)*3/4 - large_slice_angle
        large_end_angle = -(2*math.pi)/4 + large_slice_angle

        # Make our polyline.
        p = []
        p.append(start)
        p.append(knob_start)
        self.append_circle(p, v, n, knob_start + n*small_radius, small_radius,
                small_start_angle, small_end_angle)
        self.append_circle(p, v, n, mid + n*large_center_distance, large_radius,
                large_start_angle, large_end_angle)
        self.append_circle(p, -v, n, knob_end + n*small_radius, small_radius,
                small_end_angle, small_start_angle)
        p.append(knob_end)
        p.append(end)

        self.write_polyline(p, color)

