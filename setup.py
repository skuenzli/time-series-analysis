from setuptools import setup

import multiprocessing

setup(
    name='time-series-analysis',
    version='0.0.2',
    description='Contains tools for analyzing time-series data on the command-line.',
    url='https://github.com/skuenzli/time-series-analysis',
    author='Stephen Kuenzli',
    license='Apache 2.0',
    packages=['time_series_analysis'],
    zip_safe=False,
    test_suite='nose.collector',
    require=['numpy', 'pandas'],
    entry_points=dict(
        console_scripts=['analyze_series=time_series_analysis.console:main']
    ),
    tests_require=['nose', 'mock', 'unittest-xml-reporting']
)
