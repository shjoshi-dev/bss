#! /usr/local/epd/bin/python

"""Model specification for statistical tests"""

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
__copyright__ = "Copyright 2013, Shantanu H. Joshi, David Shattuck, Ahmanson Lovelace Brain Mapping Center" \
                "University of California Los Angeles"
__email__ = "s.joshi@ucla.edu"
__credits__ = 'Contributions and ideas: Shantanu H. Joshi, Roger P. Woods, David Shattuck. ' \
              'Inspired by the stats package rshape by Roger P. Woods'

import ConfigParser
import re
import sys

class ModelSpec(object):

    def __init__(self, modelfile):
        self.subjectid = ''
        self.demographics = ''
        self.fileid = ''
        self.atlas_surface = ''

        self.modeltype = ''
        self.fullmodel = ''
        self.nullmodel = ''
        self.stat_test = ''

        self.variables = ''
        self.unique = ''
        self.factors = []

        self.read_success = True
        self.read_modelfile(modelfile)

        if self.read_success == False:
            return

        self.parse_model()

    def read_modelfile(self, modelfile):
        config = ConfigParser.ConfigParser()
        config.read(modelfile)

        config.options(config.sections()[0])
        self.subjectid = config.get('subjectinfo', 'subjectid')
        self.demographics = config.get('subjectinfo', 'demographics')
        self.fileid = config.get('subjectinfo', 'fileid')
        self.atlas_surface = config.get('subjectinfo', 'atlas')

        self.read_success = False
        self.model_flag = False
        self.measure_flag = False
        try:
            self.modeltype = config.get('model', 'modeltype')
            self.fullmodel = config.get('model', 'fullmodel')
            self.nullmodel = config.get('model', 'nullmodel')
            self.stat_test = config.get('model', 'test')
            self.model_flag = True
            self.read_success = True
        except ConfigParser.NoSectionError:
            self.read_success = False

        try:
            self.coeff = config.get('measure', 'coeff')
            self.variable = config.get('measure', 'variable')
            self.stat_test = self.coeff
            self.measure_flag = True
            self.read_success = True
        except ConfigParser.NoSectionError:
            self.read_success = False

        if self.model_flag and self.measure_flag:
            sys.stdout.write('The modelspec.ini can only contain one statistical design ([model] or [measure]).'
                             'Multiple designs are not currently supported, but this may change in the future.\n')
            self.read_success = False
            return

        if self.model_flag:
            self.read_success = True
            return

        if self.measure_flag:
            self.read_success = True
            return


        # factorstring = config.get('model', 'factors')
        # for i in re.split(' ', factorstring):
        #     self.factors.append(i.rstrip().lstrip())

    def parse_model(self):
        if self.model_flag:
            # Parse fullmodel and nullmodel
            set_full = set()
            set_null = set()
            for i in re.split('\+|', self.fullmodel):
                set_full.add(i.rstrip().lstrip())
            for i in re.split('\+', self.nullmodel):
                set_null.add(i.rstrip().lstrip())
            self.unique = list(set_full - set_null)[0]  # TODO check: only one element should be present
        elif self.measure_flag:
            # self.variables = set_full | set_null
            return

    def validate_model(self):
        #TODO validate model
        pass


