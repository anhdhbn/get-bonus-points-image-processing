#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

def write_header(out, width, height, path_img=None):

    if path_img != None:
        background_img = f"""
        <defs>
            <pattern id="img1" patternUnits="userSpaceOnUse" width="{width}" height="{height}">
                <image href="{path_img}" width="{width}" height="{height}" />
            </pattern>
        </defs> 
"""
    else:
        background_img = ""

#     out.write(f"""<?xml version="1.0" encoding="utf-8"?>
# <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd" [
# <!ENTITY ns_svg "http://www.w3.org/2000/svg">
# ]>
# <svg xmlns="&ns_svg;" width="{width}" height="{height}" overflow="visible">
#     <g id="Layer_1">
# {background_img}
#     <rect width="100%" height="100%" fill="{'white' if path_img is None else 'url(#img1)'}"/>
# """ )
    out.write(f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" overflow="visible">
    <g id="Layer_1">
{background_img}
        <rect width="100%" height="100%" fill="{'white' if path_img is None else 'url(#img1)'}"/>
""" )

def write_polyline(out, p, color):
    """Write a polyline object to SVG file "out". "p" is a list of Vector objects, and
    "color" is a string representing any SVG-legal color."""

    out.write("""        <polyline fill="none" stroke="%s" stroke-width="1" points=" """ % (color,))
    for v in p:
        out.write(" %g,%g" % (v.x, v.y))
    out.write(""" "/>\n""")

def write_footer(out):
    """Write the SVG footer to the file object "out"."""

    out.write("""    </g>
</svg>
""")
