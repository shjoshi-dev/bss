#! /usr/local/epd/bin/python

"""Statsmodels interface to anova_shape"""

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

from statsmodels.formula.api import ols
from stats_output import StatsOutput
import numpy as np
import pandas
import statsmodels.api as sm


def anova_sm_func(dataframe, model):

    fit_full = ols('value' + ' ~ ' + model[0].fullmodel, data=dataframe).fit()
    fit_null = ols('value' + ' ~ ' + model[0].nullmodel, data=dataframe).fit()

    model_diff = sm.stats.anova_lm(fit_null, fit_full)
    # direction = np.sign(fit_full.tvalues[2])
    # statsout.pvalues[i] = model_diff.values[1, 5]
    # statsout.pvalues_signed[i] = direction*model_diff.values[1, 5]
    # statsout.tvalues[i] = fit_full.tvalues[2]
    # return direction*model_diff.values[1, 5]
    return fit_full.tvalues[2]/abs(fit_full.tvalues[2])*model_diff.values[1, 5]


def anova_shape_sm(model, sdata):
    statsout = StatsOutput(dim=sdata.phenotype_array.shape[1])
    pvalues = sdata.phenotype_dataframe.groupby('variable').apply(anova_sm_func, model=(model,))
    statsout.pvalues = pvalues.values
    return statsout


def anova_shape_sm_nonoptimal(model, sdata):
    statsout = StatsOutput(dim=sdata.phenotype_array.shape[1])

    for i in xrange(sdata.phenotype_array.shape[1]):

        sdata.pre_data_frame['response'] = sdata.phenotype_array[:, i]
        dataframe = pandas.DataFrame(sdata.pre_data_frame)

        fit_full = ols('response' + ' ~ ' + model.fullmodel, data=dataframe).fit()
        fit_null = ols('response' + ' ~ ' + model.nullmodel, data=dataframe).fit()

        model_diff = sm.stats.anova_lm(fit_null, fit_full)
        direction = np.sign(fit_full.tvalues[2])
        statsout.pvalues[i] = model_diff.values[1, 5]
        statsout.pvalues_signed[i] = direction*model_diff.values[1, 5]
        statsout.tvalues[i] = fit_full.tvalues[2]
    return statsout
