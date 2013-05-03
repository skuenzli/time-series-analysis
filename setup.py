from setuptools import setup

import multiprocessing

setup(
    name='time-series-analysis',
    version='0.0.1',
    description='Contains tools for analyzing time-series data on the command-line.',
    url='https://github.com/skuenzli/time-series-analysis',
    author='Stephen Kuenzli',
    license='Apache 2.0',
    packages=['time-series-analysis'],
    zip_safe=False,
    test_suite='nose.collector',
    tests_require=['nose', 'mock']
)
