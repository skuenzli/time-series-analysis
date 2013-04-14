import argparse
import sys
from pandas import *

class ControlChart:
    def __init__(self, data):
        self._series = Series(data)

    def mean(self):
        return self._series.mean()

    def median(self):
        return self._series.median()

    def std_dev(self):
        return self._series.std()

    def points_outside_lcl(self):
        lcl = self.lower_control_limit()

        enumerated_values = enumerate(self._series.values)
        return [enumerated_value for enumerated_value in enumerated_values if enumerated_value[1] < lcl]

    def points_outside_ucl(self):
        ucl = self.upper_control_limit()

        enumerated_values = enumerate(self._series.values)
        return [enumerated_value for enumerated_value in enumerated_values if enumerated_value[1] > ucl]

    def upper_control_limit(self):
        return self.mean() + (3 * self.std_dev())

    def lower_control_limit(self):
        return self.mean() - (3 * self.std_dev())

    def control_limits(self):
        return (self.lower_control_limit(), self.upper_control_limit())

class AnalyzeSeriesCommand():

    STATUS_SUCCESS = 0
    STATUS_ERROR_IO = 1

    _input_file = None
    _verbose = False
    _control_chart = None

    def _parse_options(self):
        parser = argparse.ArgumentParser(description='Analyze a series of points.')
        parser.add_argument('input_file', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
        parser.add_argument('--verbose', '-v', action='store_true')

        args = parser.parse_args()
        self._input_file = args.input_file
        self._verbose = args.verbose

    def _read_data_from_file(self, input_file):
        data = []
        if input_file:
            for line in input_file:
                try:
                    data.append(float(line.strip()))
                except ValueError as value_err:
                    sys.stderr.write("could not convert '{}' to number; encountered {}".format(line, value_err.message))
        return data

    def _print_results(self, control_chart):
        print "median: {}".format(control_chart.median())
        print "mean: {}".format(control_chart.mean())
        print "std dev: {}".format(control_chart.std_dev())
        print "lower control limit: {}".format(control_chart.lower_control_limit())
        print "upper control limit: {}".format(control_chart.upper_control_limit())
        print "points outside of lcl: {}".format(control_chart.points_outside_lcl())
        print "points outside of ucl: {}".format(control_chart.points_outside_ucl())

    def execute(self):
        self._parse_options()

        if self._verbose:
            print "Analyzing series defined in {}".format(self._input_file.name)
        try:
            data = self._read_data_from_file(self._input_file)
            if self._verbose:
                print "series data: {}".format(data)
            self._control_chart = ControlChart(data)
            self._print_results(self._control_chart)
        except IOError as io_error:
            sys.stderr.write("ERROR: {}".format(io_error.message))
            return self.STATUS_ERROR_IO

        return self.STATUS_SUCCESS
