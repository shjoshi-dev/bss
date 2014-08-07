#! /usr/local/epd/bin/python
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
__copyright__ = "Copyright 2013, Shantanu H. Joshi Ahmanson-Lovelace Brain Mapping Center, \
                 University of California Los Angeles"
__email__ = "s.joshi@ucla.edu"
__credits__ = 'Contributions and ideas: Shantanu H. Joshi, Roger P. Woods, David Shattuck. ' \
              'Inspired by the stats package rshape by Roger P. Woods'


from distutils.core import setup
# from setuptools import setup
base_dir = 'bss'
setup(
    name='bss',
    version='0.1dev',
    packages=['bss'],
    package_dir={'bss': base_dir, },
    test_suite='nose.collector',
    scripts=['bin/bss_run.py', 'bin/paired_t_test_shape.py', 'bin/bss_create_modelspec.py',
             'bin/bss_resample_surface_to_target.py', 'bin/bss_fdr.py'],
    license='MIT/TBD',
    exclude_package_data={'': ['.gitignore', '.idea']},
    author='Shantanu H. Joshi, David Shattuck',
    author_email='s.joshi@ucla.edu, shattuck@ucla.edu',
    __credits__='Contributions and ideas: Shantanu H. Joshi, Roger P. Woods, David Shattuck. '
                'Inspired by the stats package rshape by Roger P. Woods',
    description='BrainSuite statistics toolbox',
    # install_requires=[
    #     "numpy",
    #     "pandas",
    #     "statsmodels",
    #     "rpy2",
    # ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: MIT/TBD',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    keywords='BrainSuite statistics',
)
