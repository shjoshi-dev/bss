#! /usr/local/epd/bin/python
"""
Execute statistical modules in the package bss
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
__copyright__ = "Copyright 2013, Shantanu H. Joshi, David Shattuck, Ahmanson Lovelace Brain Mapping Center" \
                "University of California Los Angeles"
__email__ = "s.joshi@ucla.edu"
__credits__ = 'Contributions and ideas: Shantanu H. Joshi, Roger P. Woods, David Shattuck. ' \
              'Inspired by the stats package rshape by Roger P. Woods'


import argparse
import time
import logging
from bss.modelspec import ModelSpec
from bss.stats_data import StatsData
from bss.stats_engine import StatsEngine
import os
import sys, traceback


def main():
    parser = argparse.ArgumentParser(description='Perform statistical analysis on Brainsuite processed data.\n')
    parser.add_argument('modelspec', help='<txt file for model specification [ini]>')
    parser.add_argument('outdir', help='<output directory>')
    # parser.add_argument('-prefix', dest='outprefix', help='<output prefix>', required=False, default='left')
    # parser.add_argument('-statsengine', dest='statsengine', help='<statistical engine [R/sm]>',
    #                     required=False, choices=['R', 'sm'], default='R')
    args = parser.parse_args()
    args.statsengine = 'R'
    t = time.time()

    bss_run(args.modelspec, args.outdir, args.statsengine)
    elapsed = time.time() - t
    os.sys.stdout.write("Elapsed time " + str(elapsed) + " sec.")


def bss_run(modelspec, outdir, opt_statsengine):

    try:
        outprefix = ''
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        logging.basicConfig(filename=os.path.join(outdir, 'bss.log'), level=logging.DEBUG,
                            format='%(levelname)s:%(message)s', filemode='w')
        logging.info('Reading model file ' + modelspec)
        model = ModelSpec(modelspec)
        logging.info('Done.')
        if model.read_success == False:
            # sys.stdout.write('The modelspec file is incorrectly formatted. Perhaps it is missing some sections/fields.\n')
            return

        logging.info('Reading demographics file ' + model.demographics + ' and creating a data frame...')
        statsdata = StatsData(model.demographics, model)
        if statsdata.data_read_flag:
            logging.info('Done.')
            # Save the phenotype array to a ascii file for debugging
            statsdata.write_subject_phenotype_array(os.path.join(outdir, 'phenotype_array.mat'))
            logging.info('Computing ' + model.modeltype + ' with ' + model.stat_test + '...')
            statsengine = StatsEngine(model, statsdata, engine=opt_statsengine)
            statsoutput = statsengine.run()
            if model.measure_flag:
                outprefix = model.stat_test + '_' + model.variable + '_' + os.path.splitext(os.path.split(model.atlas_surface)[1])[0]
            elif model.model_flag:
                outprefix = model.stat_test + '_' + model.unique  + '_' + os.path.splitext(os.path.split(model.atlas_surface)[1])[0]
            statsoutput.save(outdir, outprefix, model.atlas_surface)
            logging.info('Done.')
        else:
            sys.stdout.write('Problem in reading all the cortical attributes. '
                             'Please check if the individual cortical surfaces are registered to the same atlas.\n')
            sys.stdout.write('Exiting the statistical analysis.\n')
    except:
        print "Something went wrong. Please send this error message to the developers." \
              "\nUnexpected error:", sys.exc_info()[0]
        print traceback.print_exc(file=sys.stdout)


if __name__ == '__main__':
    main()