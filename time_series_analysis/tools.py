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

    def get_last_point(self):
        last_index = self._series.last_valid_index()
        last_value = self._series.get_value(last_index)
        return (last_index, last_value)

    def is_last_point_in_control(self):
        (index, value) = self.get_last_point()
        return self.lower_control_limit() <= value <= self.upper_control_limit()


class AnalyzeSeriesCommand():

    # /usr/include/sysexits.h is primary source of inspiration for status exit
    STATUS_SUCCESS = 0
    STATUS_ASSERTION_FAILED = 1
    STATUS_ERROR_IO = 74

    def __init__(self):
        self._argument_parser = AnalyzeSeriesCommand._create_argument_parser()
        self._assert_last_point_in_control = False
        self._input_file = None
        self._verbose = False
        self._control_chart = None

    @staticmethod
    def _create_argument_parser():
        description = """analyze a series of points and print descriptive statistics"""
        epilog = """analyze_series supports:
  * integer and floating-point numbers
  * positive and negative numbers
  * whitespace around the number
  * statistics useful for analysis of time-series data:
    * median
    * mean, sample standard deviation
    * upper and lower control limits
    * points and associated value falling outside of control limits"""
        parser = argparse.ArgumentParser(description=description, epilog=epilog,
            formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument('input_file', nargs='?', type=argparse.FileType('r'),
            default=sys.stdin, help="input file to process, defaults to standard input")
        parser.add_argument('-v', '--verbose', action='store_true', help='print additional debug information')
        parser.add_argument('--assert-last-point-in-control', action='store_true',
            help="assert the last point in the series is in-control and exit with status code '2' if last point is not in control")
        return parser

    def _parse_options(self):

        args = self._argument_parser.parse_args()
        self._input_file = args.input_file
        self._verbose = args.verbose
        self._assert_last_point_in_control = args.assert_last_point_in_control

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
        lcl = control_chart.points_outside_lcl()
        ucl = control_chart.points_outside_ucl()

        print "median: {}".format(control_chart.median())
        print "mean: {}".format(control_chart.mean())
        print "std dev: {}".format(control_chart.std_dev())
        print "lower control limit: {}".format(control_chart.lower_control_limit())
        print "upper control limit: {}".format(control_chart.upper_control_limit())
        print self._format_control_limit_results("lcl", lcl)
        print self._format_control_limit_results("ucl", ucl)

        if self._assert_last_point_in_control and not self._control_chart.is_last_point_in_control():
            (index, value) = self._control_chart.get_last_point()
            return (AnalyzeSeriesCommand.STATUS_ASSERTION_FAILED, "last point (index={index}, value={value}) is out of control".format(index=index, value=value))

        return (AnalyzeSeriesCommand.STATUS_SUCCESS, "")

    def _format_control_limit_results(self, name_of_cl, points_outside_cl):
        if(len(points_outside_cl)) > 0:
            param = points_outside_cl
        else:
            param = None

        return "points outside of {name_of_cl}: {points}".format(name_of_cl=name_of_cl, points=param)


    def execute(self):
        self._parse_options()

        if self._verbose:
            print "Analyzing series defined in {}".format(self._input_file.name)

        try:
            data = self._read_data_from_file(self._input_file)
            if self._verbose:
                print "series data: {}".format(data)
            self._control_chart = ControlChart(data)
            status_and_message = self._print_results(self._control_chart)
        except IOError as io_error:
            status_and_message = (self.STATUS_ERROR_IO, "ERROR: {}".format(io_error.message))

        return status_and_message