#! /usr/local/epd/bin/python

"""Data specification for statistical tests"""

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


class StatsData(object):

    def __init__(self, demographics_file, model):
        self.demographic_data = ''
        self.dataframe = None
        self.phenotype_files = []
        self.phenotype_array = None
        self.pre_data_frame = {}
        self.surface_average = None
        self.phenotype_dataframe = None
        # self.attribue_matrix = None

        self.read_demographics(demographics_file)

        if not model.phenotype_attribute_matrix_file and not model.phenotype:
            sys.stdout.write('Error: Phenotype is not set. Data frame will not be created.')
            return

        # Choose the phenotype_attribute_matrix binary data if phenotype is also set
        if model.phenotype_attribute_matrix_file and model.phenotype:
            self.read_subject_phenotype_attribute_matrix(model)
            self.create_data_frame(model)
            return

        if model.phenotype:
            self.read_subject_phenotype(model)

        self.create_data_frame(model)

    def read_demographics(self, demographics_file):
        filename, ext = os.path.splitext(demographics_file)
        if ext == '.csv':
            self.demographic_data = pandas.read_csv(demographics_file)
        elif ext == '.txt':
            self.demographic_data = pandas.read_table(demographics_file)

    def validate_data(self):
        #TODO routines for validating self.demographic_data
        pass

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

    def create_data_frame(self, model):
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
        for i in xrange(self.phenotype_array.shape[1]):
            colnames.append('V'+str(i))

        temp_frame = pandas.DataFrame(self.phenotype_array)
        temp_frame.columns = colnames
        temp_frame[model.subjectid] = self.demographic_data[model.subjectid]

        tot_dataframe = pandas.merge(self.demographic_data, temp_frame)
        tot_dataframe = pandas.melt(tot_dataframe, id_vars=self.demographic_data.columns)
        self.phenotype_dataframe = tot_dataframe
        return

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
    def read_aggregated_attributes_from_surfacefilelist(surfacefilelist):

        # Read first file
        s1 = dfsio.readdfs(surfacefilelist[0])
        # s1 = Surface()
        # s1.read(surfacefilelist[0])
        attributes_new = s1.attributes

        num_files = len(surfacefilelist)
        attrib_size = len(attributes_new)

        attribute1_array = np.empty((num_files, attrib_size), 'float')
        attribute1_array[0, :] = attributes_new

        average_coords = s1.coords

        for i in range(1, len(surfacefilelist)):
            s1.read(surfacefilelist[i])
            average_coords += s1.coords
            if len(s1.attributes) != attrib_size:
                sys.stdout.write("Length of attributes in Files " + surfacefilelist[i] + " and " + surfacefilelist[0]
                                 + " do not match. Quitting.\n")
                attribute1_array = []
                return attribute1_array
            else:
                attribute1_array[i, :] = s1.attributes

        average_coords /= len(surfacefilelist)
        s1_average = s1
        s1_average.coords = average_coords

        return s1, s1_average, attribute1_array

    @staticmethod
    def read_aggregated_attributes_from_surfaces(filename):
        data_list = pandas.read_table(filename, sep='\t')
        surfacefile_list = data_list['File']
        return StatsData.read_aggregated_attributes_from_surfacefilelist(surfacefile_list)

