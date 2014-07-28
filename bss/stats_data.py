#! /usr/local/epd/bin/python

"""Data specification for statistical tests"""

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

import dfsio
from glob import glob
import struct
import array
import os
import numpy as np
import rpy2.robjects as robjects
import pandas
import sys
import scipy.io


class StatsData(object):

    def __init__(self, demographics_file, model, max_block_size=2000):
        self.demographic_data = ''
        self.dataframe = None
        self.phenotype_files = []
        self.phenotype_array = None
        self.pre_data_frame = {}
        self.surface_average = None
        self.phenotype_dataframe = None
        # self.attribue_matrix = None
        self.phenotype_array = []
        self.demographic_data = self.read_demographics(demographics_file)
        self.data_read_flag = False
        self.max_block_size = max_block_size

        # if not model.phenotype_attribute_matrix_file and not model.phenotype:
        #     sys.stdout.write('Error: Phenotype is not set. Data frame will not be created.')
        #     return

        # # Choose the phenotype_attribute_matrix binary data if phenotype is also set
        # if model.phenotype_attribute_matrix_file and model.phenotype:
        #     self.read_subject_phenotype_attribute_matrix(model)
        #     self.create_data_frame(model)
        #     return

        # if model.phenotype:
        #     self.read_subject_phenotype(model)

        s1_atlas = dfsio.readdfs(model.atlas_surface)
        self.phenotype_array = self.read_aggregated_attributes_from_surfacefilelist(self.demographic_data[model.fileid],
                                                                                    s1_atlas.vertices.shape[0])

        if len(self.phenotype_array) == 0:
            self.data_read_flag = False
        else:
            self.data_read_flag = True
            # self.create_data_frame(model)

            self.blocks_idx = []
            # At this point the data is completely read, so create indices of blocks
            if self.phenotype_array.shape[1] > self.max_block_size:
                quotient, remainder = divmod(self.phenotype_array.shape[1], self.max_block_size)
                for i in np.arange(quotient)+1:
                    self.blocks_idx.append(((i-1)*self.max_block_size, (i-1)*self.max_block_size + self.max_block_size))
                if remainder != 0:
                    i = quotient + 1
                    self.blocks_idx.append(((i-1)*self.max_block_size, (i-1)*self.max_block_size + remainder))
            else:
                self.blocks_idx.append((0, self.phenotype_array.shape[1]))
            return



    @classmethod
    def read_demographics(cls, demographics_file):
        filename, ext = os.path.splitext(demographics_file)
        if ext == '.csv':
            demographic_data = pandas.read_csv(demographics_file)
        elif ext == '.txt':
            demographic_data = pandas.read_table(demographics_file)
        return demographic_data

    def validate_data(self):
        #TODO routines for validating self.demographic_data
        pass

    def read_subject_file(self, model):
        for filename in self.demographic_data[model.fileid]:
            self.phenotype_files.append(filename)
        s1, s1_average, self.phenotype_array = self.read_aggregated_attributes_from_surfacefilelist(self.phenotype_files)
        return

    def read_subject_phenotype(self, model):
        for subjectid in self.demographic_data[model.subjectid]:
            self.phenotype_files.append(glob(os.path.join(model.subjdir, subjectid, '*' + model.phenotype + '*'))[0])

        s1, s1_average, self.phenotype_array = dfsio.read_aggregated_attributes_from_surfacefilelist(self.phenotype_files)
        self.surface_average = s1_average

    def read_subject_phenotype_attribute_matrix(self, model):
        fid = open(model.phenotype_attribute_matrix_file, 'rb')
        rows = np.array(struct.unpack('i', fid.read(4)), dtype='uint32')[0]  #size(int32) = 4 bytes
        cols = np.array(struct.unpack('i', fid.read(4)), dtype='uint32')[0]  #size(int32) = 4 bytes
        arrayfloat = array.array('f')
        arrayfloat.fromfile(fid, rows*cols)
        self.phenotype_array = np.frombuffer(arrayfloat, dtype=np.float32, offset=0).reshape(cols, rows, order='F')
        fid.close()

    def write_subject_phenotype_array(self, filename):
        scipy.io.savemat(filename, {'data_array': self.phenotype_array})

    def create_data_frame(self, model):
        for i in model.variables:
            self.pre_data_frame[i] = self.demographic_data[i]

            # if i in model.factors:
            #     self.pre_data_frame[i] = self.demographic_data[i]
            # else:
            #     # Use either one of Int, Str, or Float vectors
            #     if self.demographic_data[i][0].dtype.type in (np.int32, np.int64):
            #         self.pre_data_frame[i] = self.demographic_data[i]
            #     elif self.demographic_data[i][0].dtype.type in (np.float32, np.float64): #TODO check this
            #         self.pre_data_frame[i] = self.demographic_data[i]
        # Create the phenotype array data frame
        # Create the column names for vertices automatically
        colnames = []
        for i in xrange(self.phenotype_array.shape[1]):
            colnames.append('V'+str(i))

        temp_frame = pandas.DataFrame(self.phenotype_array)
        temp_frame.columns = colnames
        temp_frame[model.subjectid] = self.demographic_data[model.subjectid]

        tot_dataframe = pandas.merge(self.demographic_data, temp_frame)
        tot_dataframe = pandas.melt(tot_dataframe, id_vars=self.demographic_data.columns)
        self.phenotype_dataframe = tot_dataframe
        return

    def get_data_frame_block(self, model, block_num):
        for i in model.variables:
            if i in model.factors:
                self.pre_data_frame[i] = self.demographic_data[i]
            else:
                # Use either one of Int, Str, or Float vectors
                if self.demographic_data[i][0].dtype.type in (np.int32, np.int64):
                    self.pre_data_frame[i] = self.demographic_data[i]
                elif self.demographic_data[i][0].dtype.type in (np.float32, np.float64): #TODO check this
                    self.pre_data_frame[i] = self.demographic_data[i]
        # Create the phenotype array data frame
        # Create the column names for vertices automatically
        colnames = []

        for i in range(self.blocks_idx[block_num][0], self.blocks_idx[block_num][1]):
            colnames.append('V'+str(i))

        temp_frame = pandas.DataFrame(self.phenotype_array[:, range(self.blocks_idx[block_num][0], self.blocks_idx[block_num][1])])
        temp_frame.columns = colnames
        temp_frame[model.subjectid] = self.demographic_data[model.subjectid]

        tot_dataframe = pandas.merge(self.demographic_data, temp_frame)
        tot_dataframe = pandas.melt(tot_dataframe, id_vars=self.demographic_data.columns)
        return tot_dataframe

    def convert_pandas_to_r_data_frame(self, model, dataframe):
        pre_data_frame = {}
        for i in dataframe.columns:
            if i in model.factors:
                pre_data_frame[i] = robjects.FactorVector(dataframe[i])
            else:
                # Use either one of Int, Str, or Float vectors
                if dataframe[i].dtype.type in (np.int32, np.int64):
                    pre_data_frame[i] = robjects.IntVector(dataframe[i])
                elif dataframe[i].dtype.type in (np.float32, np.float64):
                    pre_data_frame[i] = robjects.FloatVector(dataframe[i])
                else:
                    pre_data_frame[i] = robjects.FactorVector(dataframe[i])

        return robjects.DataFrame(pre_data_frame)

    def get_r_data_frame_block(self, model, block_num):
        df = self.get_data_frame_block(model, block_num)
        return self.convert_pandas_to_r_data_frame(model, df)

    def get_r_pre_data_frame(self, model):
        pre_data_frame = {}
        for i in self.phenotype_dataframe.columns:
            if i in model.factors:
                pre_data_frame[i] = robjects.FactorVector(self.phenotype_dataframe[i])
            else:
                # Use either one of Int, Str, or Float vectors
                if self.phenotype_dataframe[i].dtype.type in (np.int32, np.int64):
                    pre_data_frame[i] = robjects.IntVector(self.phenotype_dataframe[i])
                elif self.phenotype_dataframe[i].dtype.type in (np.float32, np.float64):
                    pre_data_frame[i] = robjects.FloatVector(self.phenotype_dataframe[i])
                else:
                    pre_data_frame[i] = robjects.FactorVector(self.phenotype_dataframe[i])

        return robjects.DataFrame(pre_data_frame)

    def create_r_pre_data_frame(self, model):
        pre_data_frame = {}
        for i in model.variables:
            if i in model.factors:
                pre_data_frame[i] = robjects.FactorVector(self.demographic_data[i])
            else:
                # Use either one of Int, Str, or Float vectors
                if self.demographic_data[i][0].dtype.type is np.int64:
                    pre_data_frame[i] = robjects.IntVector(self.demographic_data[i])
                elif self.demographic_data[i][0].dtype.type is np.float64:
                    pre_data_frame[i] = robjects.FloatVector(self.demographic_data[i])

        return pre_data_frame

    @staticmethod
    def read_aggregated_attributes_from_surfacefilelist(surfacefilelist, attrib_siz):
        attribute_array = np.empty((len(surfacefilelist), attrib_siz), 'float')
        for i in range(0, len(surfacefilelist)):
            attributes = dfsio.readdfsattributes(surfacefilelist[i])
            if len(attributes) != attrib_siz:
                sys.stdout.write("Length of attributes in Files " + surfacefilelist[i] + " and " + surfacefilelist[0]
                                 + " do not match. Quitting.\n")
                attribute_array = []
                return attribute_array
            else:
                attribute_array[i, :] = attributes
        return attribute_array

    @staticmethod
    def read_aggregated_attributes_from_surfaces(filename):
        data_list = pandas.read_table(filename, sep='\t')
        surfacefile_list = data_list['File']
        return StatsData.read_aggregated_attributes_from_surfacefilelist(surfacefile_list)

