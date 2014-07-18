#! /usr/local/epd/bin/python

"""
Execute statistical modules in the package bss
"""

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
import sys


def main():
    parser = argparse.ArgumentParser(description='Perform statistical analysis on Brainsuite processed data.\n')
    parser.add_argument('modelspec', help='<txt file for model specification [ini]>')
    parser.add_argument('outdir', help='<output directory>')
    # parser.add_argument('-prefix', dest='outprefix', help='<output prefix>', required=False, default='left')
    parser.add_argument('-statsengine', dest='statsengine', help='<statistical engine [R/sm]>',
                        required=False, choices=['R', 'sm'], default='R')

    args = parser.parse_args()
    t = time.time()
    bss_run(args.modelspec, args.outdir, args.statsengine)
    elapsed = time.time() - t
    os.sys.stdout.write("Elapsed time " + str(elapsed) + " sec.")


def bss_run(modelspec, outdir, opt_statsengine):

    outprefix = ''
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    logging.basicConfig(filename=os.path.join(outdir, 'bss.log'), level=logging.DEBUG,
                        format='%(levelname)s:%(message)s', filemode='w')
    logging.info('Reading model file ' + modelspec)
    model = ModelSpec(modelspec)
    logging.info('Done.')
    if model.read_success == False:
        sys.stdout.write('The modelspec file is incorrectly formatted. Perhaps it is missing some sections/fields.\n')
        sys.exit()

    logging.info('Reading demographics file ' + model.demographics + ' and creating a data frame...')
    statsdata = StatsData(model.demographics, model)
    logging.info('Done.')

    if statsdata.data_read_flag:
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

if __name__ == '__main__':
    main()