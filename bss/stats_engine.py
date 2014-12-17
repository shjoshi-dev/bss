#! /usr/local/epd/bin/python

"""Class that encapsulates the underlying statistical engine that will execute statistical tests"""

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
__copyright__ = "Copyright 2013, Shantanu H. Joshi, David Shattuck, Ahmanson Lovelace Brain Mapping Center"\
                "University of California Los Angeles"
__email__ = "s.joshi@ucla.edu"
__credits__ = 'Contributions and ideas: Shantanu H. Joshi, Roger P. Woods, David Shattuck. ' \
              'Inspired by the stats package rshape by Roger P. Woods'

from anova_shape_sm import anova_shape_sm
from anova_shape_r import anova_shape_r
from anova_shape_r import anova_shape_r_block
from corr_r import corr_shape_r_block
from corr_r import corr_shape_r
from corr_r import corr_fast
import sys


class StatsEngine(object):

    def __init__(self, model, stats_data, engine='sm'):
        self.engine = engine
        self.model = model
        self.stats_data = stats_data
        self.commands_statmodels = None
        self.commands_r = None
        self.define_stats_commands()

    def define_stats_commands(self):
        if self.engine == 'sm':
            self.commands = {'anova': anova_shape_sm, }
        elif self.engine == 'R':
            self.commands = {'anova': anova_shape_r_block,
                             'corr': corr_fast,
                             }

    def run(self):
        sys.stdout.write('Running the statistical model. This may take a while...')
        stats_out = self.commands[self.model.stat_test](self.model, self.stats_data)
        sys.stdout.write('Done.\n')
        return stats_out
