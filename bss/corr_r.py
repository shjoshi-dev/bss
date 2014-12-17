#! /usr/local/epd/bin/python

"""R interface to correlation"""

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
__copyright__ = "Copyright 2014, Shantanu H. Joshi Ahmanson-Lovelace Brain Mapping Center, \
                 University of California Los Angeles"
__email__ = "s.joshi@ucla.edu"
__credits__ = 'Inspired by the stats package rshape by Roger P. Woods'

import rpy2.robjects as robjects
import numpy as np
from stats_output import StatsOutput
from rpy2.robjects import r
r.library("data.table")
from sys import stdout


def corr_r_func():

    corr_r_funct_str = {'corr_r_func': '''<- function(x, y, methodstr)
                {
                    return(cor.test(x, y, method=methodstr))
                }
                '''}
    return corr_r_funct_str


def corr_shape_r(model, sdata):
    statsout = StatsOutput(dim=sdata.phenotype_array.shape[1])
    r_dataframe = sdata.get_r_pre_data_frame(model)
    robjects.r.assign('r_dataframe', r_dataframe)
    robjects.r(corr_r_func().keys()[0] + corr_r_func()[corr_r_func().keys()[0]])
    robjects.r('r_datatable <- data.table(r_dataframe)')

    varx = 'value'
    vary = model.variable
    r_corr_cmd = 'result <- r_datatable[, as.list({0:s}({1:s}, {2:s}, \"{3:s}\")), by=variable]'.format(
        corr_r_func().keys()[0], varx, vary, "pearson")
    robjects.r(r_corr_cmd)

    result = robjects.globalenv['result']

    statsout.pvalues = np.array(result[list(result.names).index('p.value')])
    corr_coeff = np.array(result[list(result.names).index('estimate')])
    corr_coeff = corr_coeff[1:len(corr_coeff):2]
    statsout.pvalues = np.sign(corr_coeff)*statsout.pvalues[1:len(statsout.pvalues):2]
    statsout.corrvalues = corr_coeff
    return statsout


def corr_shape_r_block(model, sdata):
    siz = sdata.phenotype_array.shape[1]
    statsout = StatsOutput(dim=siz)
    pvalues = np.ones(siz)
    corr_coeff = np.zeros(siz)
    stdout.write('Computing correlations for blocks...')
    stdout.flush()
    for block_num, block_idx in enumerate(sdata.blocks_idx):
        stdout.write(str(block_num) + ', ')
        stdout.flush()
        r_dataframe = sdata.get_r_data_frame_block(model, block_num)
        robjects.r.assign('r_dataframe', r_dataframe)
        robjects.r(corr_r_func().keys()[0] + corr_r_func()[corr_r_func().keys()[0]])
        robjects.r('r_datatable <- data.table(r_dataframe)')

        varx = 'value'
        vary = model.variable
        r_corr_cmd = 'result <- r_datatable[, as.list({0:s}({1:s}, {2:s}, \"{3:s}\")), by=variable]'.format(
            corr_r_func().keys()[0], varx, vary, "pearson")
        robjects.r(r_corr_cmd)
        result = robjects.globalenv['result']

        temp = np.array(result[list(result.names).index('p.value')])
        pvalues[range(block_idx[0], block_idx[1])] = temp[1:len(temp):2]

        temp = np.array(result[list(result.names).index('estimate')])
        corr_coeff[range(block_idx[0], block_idx[1])] = temp[1:len(temp):2]

    pvalues[np.isnan(pvalues)] = 1
    corr_coeff[np.isnan(corr_coeff)] = 0
    stdout.write('Done.\n')
    # stdout.write('Saving output files...\n')
    stdout.flush()
    statsout.pvalues = np.sign(corr_coeff)*pvalues
    statsout.pvalues[np.isnan(corr_coeff)] = 1  # Set the p-values with the nan correlations to 1
    statsout.corrvalues = corr_coeff
    statsout.file_name_string = '_corr_with_' + model.variable
    return statsout


def corr_fast(model, sdata):
    def fastColumnWiseCorrcoef(O, P): #P = age_mtx = 1 x n, O = subjects_vertices_mtx = n x m
        n = P.size
        DO = O - (np.einsum('ij->j',O) / np.double(n))
        P -= (np.einsum('i->',P) / np.double(n))
        tmp = np.einsum('ij,ij->j',DO,DO)
        tmp *= np.einsum('i,i->',P,P)
        return np.dot(P, DO) / np.sqrt(tmp)
    def slowColumnWiseCorrcoef(O, P): #P = age_mtx = 1 x n, O = subjects_vertices_mtx = n x m
        n = P.size
        DO = O - (np.sum(O, 0) / np.double(n))
        DP = P - (np.sum(P) / np.double(n))
        return np.dot(DP, DO) / np.sqrt(np.sum(DO ** 2, 0) * np.sum(DP ** 2))

    size = sdata.phenotype_array.shape[1]
    statsout = StatsOutput(dim=size)
    O = sdata.phenotype_array
    P = np.array(sdata.demographic_data[model.variable])
    #P = np.array([49,30,37,62,23,23,59,33,52,59,33,52,34,49,21,22,23,24,47,41,26,23,55,22,47,21,61,38,30,42,32,48,33,66,63,23,64,55,54,27,31,51,21,53,54,54,50,47,31,42,56,33,32,34,32,34,21,60,62,41,66,69,63,49,45,64,45,41,40,48,48,56,48,53,55,47,24,55,21,52,61,60,32,61,32,69,61,60,60])
    #print P.shape
    corr_coeff = slowColumnWiseCorrcoef(O, P)
    statsout.pvalues = np.empty(size)
    statsout.pvalues.fill(0.01)
    statsout.pvalues = 1*np.random.random(size) - 0.5
    statsout.corrvalues = corr_coeff
    statsout.file_name_string = '_corr_with_' + model.variable
    print "statsout.pvalues.shape = " + str(statsout.pvalues.shape)
    print "statsout.corrvalues.shape = " + str(statsout.corrvalues.shape)
    print statsout.pvalues
    print statsout.corrvalues
    #np.savetxt("corr_fast.csv", statsout.corrvalues, delimiter=",")

    return statsout