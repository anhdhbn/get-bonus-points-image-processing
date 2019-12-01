#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import base
# import os

from anhdh.makecutpath.Maker import Maker
from anhdh.cut_display.Cutter import Cutter
from anhdh.cut_display.Presenter import Presenter
from anhdh.solve.original.Original import Original
from anhdh.solve.without_original.WithoutOriginal import WithoutOriginal

path = "./5.jpg"

maker = Maker(path)
maker.make_cut_path()

cutter = Cutter(path)
cutter.process()

presenter = Presenter(path)
presenter.Display()

original = Original(path)
original.solve()

withoutOriginal = WithoutOriginal(path)
withoutOriginal.solve()
