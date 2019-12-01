#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import base
# import os

# jpc = base.JigsawPieceClipsSVG(
#                 width=1080,
#                 height=720,
#                 pieces=200,
#                 minimum_piece_size=150)
# svgfile = os.path.join("./", 'lines.svg')
# f = open(svgfile, 'w')
# f.write(jpc.svg())
# f.close()

from anhdh.makecutpath.Maker import Maker
from anhdh.cut_display.Cutter import Cutter
from anhdh.cut_display.Presenter import Presenter
from anhdh.solve.original.Original import Original
from anhdh.solve.without_original.Piece  import Piece
from anhdh.solve.without_original.WithoutOriginalSolver  import WithoutOriginalSolver

path = "./1.jpg"

maker = Maker(path)
maker.make_cut_path()

cutter = Cutter(path)
cutter.process()

presenter = Presenter(path)
presenter.Display()

original = Original(path)
original.solve()

# withoutOriginalSolver = WithoutOriginalSolver(path)
# withoutOriginalSolver.solve()
