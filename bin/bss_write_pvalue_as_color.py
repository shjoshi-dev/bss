#! /usr/local/epd/bin/python

"""
Convert p-values to rgb color
"""
"""Copyright (C) Shantanu H. Joshi, David Shattuck,
Brain Mapping Center, University of California Los Angeles

Bss is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

Bss is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA."""

__author__ = "Shantanu H. Joshi"
__copyright__ = "Copyright 2014, Shantanu H. Joshi, David Shattuck, Ahmanson Lovelace Brain Mapping Center" \
                "University of California Los Angeles"
__email__ = "s.joshi@ucla.edu"
__credits__ = 'Contributions and ideas: Shantanu H. Joshi, Roger P. Woods, David Shattuck. ' \
              'Inspired by the stats package rshape by Roger P. Woods'


import argparse
from bss import dfsio
from bss import colormaps
import os
import sys
import numpy as np


def main():
    parser = argparse.ArgumentParser(description='Convert p-values to rgb color. Assumes p-values already exist as attributes in the dfs file.\n')
    parser.add_argument('dfs_surface_in', help='<input dfs surface>')
    parser.add_argument('dfs_surface_out', help='<output dfs surface>')

    args = parser.parse_args()
    bss_write_pvalue_as_log_color(args.dfs_surface_in, args.dfs_surface_out)


def bss_write_pvalue_as_log_color(surfin, surfout):

    s1 = dfsio.readdfs(surfin)

    if not hasattr(s1, 'attributes'):
        sys.stdout.write('Error: The surface ' + surfin + ' is missing p-value attributes.\n')
        sys.exit(0)

    cmap = colormaps.Colormap('pvalue', s1.attributes)
    rgb_list = cmap.get_rgb_list_from_attribute_list(s1.attributes)

    s1.vColor = np.empty((3, len(s1.attributes)))
    for idx, val in enumerate(rgb_list):
        s1.vColor[:, idx] = [val[0], val[1], val[2]]
        # s1.vColor[:, idx] = [abs(np.random.random()), abs(np.random.random()), abs(np.random.random())]
    s1.vColor = np.ndarray.transpose(s1.vColor)
    exportParaviewCmap(cmap.color_dict, surfout + '.xml')
    dfsio.writedfs(surfout, s1)


def exportParaviewCmap(cdict,filename):
    fid = open(filename,'wt')
    fid.write('<ColorMap name="bi-direct" space="RGB">\n')

    for i in range(0,len(cdict['red'])):
        xval,r,g,b = cdict['red'][i][0],cdict['red'][i][1],cdict['green'][i][1],cdict['blue'][i][1]
        fid.write('<Point x="{0:f}" o="1" r="{1:f}" g="{2:f}" b="{3:f}"/>\n'.format(float(xval),float(r),float(g),float(b)))

    fid.write('<NaN r="1" g="1" b="0"/>\n')
    fid.write('</ColorMap>\n')
    return None


if __name__ == '__main__':
    main()
