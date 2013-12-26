#! /usr/local/epd/bin/python

"""Output specification for statistical tests"""

__author__ = "Shantanu H. Joshi"
__copyright__ = "Copyright 2013, Shantanu H. Joshi, David Shattuck, Ahmanson Lovelace Brain Mapping Center"\
                "University of California Los Angeles"
__email__ = "s.joshi@ucla.edu"
__credits__ = 'Contributions and ideas: Shantanu H. Joshi, Roger P. Woods, David Shattuck. ' \
              'Inspired by the stats package rshape by Roger P. Woods'

import numpy as np
import os
import dfsio
import sys


class StatsOutput(object):

    def __init__(self, dim=0):
        self.pvalues = np.zeros(dim)
        self.pvalues_signed = np.zeros(dim)
        self.tvalues = np.zeros(dim)

    def save(self, outdir, outprefix, atlas_filename):

        s1 = dfsio.readdfs(atlas_filename)

        s1.attributes = self.pvalues
        print s1.attributes

        if len(s1.attributes) == s1.vertices.shape[0]:
            dfsio.writedfs(os.path.join(outdir, outprefix + '_atlas_stats.dfs'), s1)
        else:
            sys.stdout.write('Error: Dimension mismatch between the p-values and the number of vertices. '
                             'Quitting without saving.\n')
