#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math

class Vector:
    """2D vector class."""

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __str__(self):
        return "(%g,%g)" % (self.x, self.y)

    def __repr__(self):
        return str(self)

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Vector(self.x*other, self.y*other)

    def __div__(self, other):
        return Vector(self.x/other, self.y/other)

    def __truediv__(self, other):
        return Vector(self.x/other, self.y/other)

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalized(self):
        return self/self.length()

    def reciprocal(self):
        """Xoay 90 ngược chiều kim đồng hồ."""
        return Vector(-self.y, self.x)