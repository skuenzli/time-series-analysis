#!tsa-virtualenv/bin/python

from random import choice
import sys
import unittest
import tempfile
from mock import MagicMock
import xmlrunner

from time_series_analysis import ControlChart, AnalyzeSeriesCommand

class ControlChartTest(unittest.TestCase):

    # calculated values sourced from wolfram alpha

    def setUp(self):
        self.series_under_control = [
            10.0, 9.0, 8.5, 11.5, 10.25, 9.75, 10.1, 9.9, 11, 10.5
        ]

        self.series_with_ucl_outliers = [
            -1, 0, 1, -1, 0, 1, -1, 0, 1
            , -1, 0, 1, -1, 0, 1, -1, 0, 1
            , -1, 0, 1, -1, 0, 1, -1, 0, 1
            , 4
        ]

        self.series_with_lcl_outliers = [
            -4
            , -1, 0, 1, -1, 0, 1, -1, 0, 1
            , -1, 0, 1, -1, 0, 1, -1, 0, 1
            , -1, 0, 1, -1, 0, 1, -1, 0, 1
        ]

    def test_series_under_control(self):
        chart = ControlChart(self.series_under_control)

        self.assertEquals(10.05, chart.mean())
        self.assertEquals(10.05, chart.median())
        self.assertAlmostEquals(0.8737, chart.std_dev(), places=4)

        self.assertAlmostEquals(7.429, chart.lower_control_limit(), places=3)
        self.assertAlmostEquals(12.671, chart.upper_control_limit(), places=3)

        self.assertEquals([], chart.points_outside_lcl())
        self.assertEquals([], chart.points_outside_ucl())

    def test_points_outside_lcl_are_identified(self):
        chart = ControlChart(self.series_with_lcl_outliers)

        index = 0
        value = -4
        self.assertIn((index, value), chart.points_outside_lcl())

    def test_points_outside_ucl_are_identified(self):
        chart = ControlChart(self.series_with_ucl_outliers)

        index = 27
        value = 4
        self.assertIn((index, value), chart.points_outside_ucl())

    def test_chart_computes_sample_statistics(self):
        chart = ControlChart(self.series_with_ucl_outliers)

        self.assertAlmostEqual(0.1429, chart.mean(), places=4)
        self.assertEquals(0, chart.median())
        self.assertAlmostEqual(1.113, chart.std_dev(), places=3)

    def test_chart_computes_control_limits(self):
        chart = ControlChart(self.series_with_ucl_outliers)

        (lcl, ucl) = chart.control_limits()

        self.assertEquals(lcl, chart.lower_control_limit())
        self.assertEquals(ucl, chart.upper_control_limit())

        self.assertAlmostEqual(lcl, -3.1952, places=4)
        self.assertAlmostEqual(ucl, 3.4809, places=4)


class AnalyzeSeriesCommandTest(unittest.TestCase):

    def setUp(self):
        self._analyze_series_cmd = AnalyzeSeriesCommand()
        self._series = [ 10, 9, 8.5, 11.5, 10.25, 9.75, 10.1, 9.9, 8.75, 10.5 ]

    def test_properties_when_no_arguments_provided(self):
        sys.argv = ["analyze_series"]
        cmd = AnalyzeSeriesCommand()

        cmd._parse_options()

        self.assertEquals(sys.stdin, cmd._input_file)
        self.assertFalse(cmd._verbose)

    def test_properties_when_arguments_provided(self):
        tf = tempfile.NamedTemporaryFile(mode="r")

        sys.argv = ["analyze_series", tf.name]

        verbosity = choice([True, False])
        if verbosity:
            sys.argv.append("--verbose")

        cmd = AnalyzeSeriesCommand()

        cmd._parse_options()

        self.assertEquals(tf.name, cmd._input_file.name)
        self.assertEquals(verbosity, cmd._verbose)

    def test_parseOptions_called_when_executed(self):
        mock_parse_options = MagicMock()
        self._analyze_series_cmd._parse_options = mock_parse_options

        self._analyze_series_cmd.execute()

        mock_parse_options.assert_called_once_with()

    def test_data_series_is_analyzed(self):
        tf = tempfile.NamedTemporaryFile()
        control_chart = ControlChart(self._series)

        input = ""
        for val in self._series:
            input += " {} \n".format(str(val))

        tf.write(input)
        tf.flush()

        sys.argv = ["analyze_series", tf.name, "--verbose"]

        status = self._analyze_series_cmd.execute()

        self.assertEquals(AnalyzeSeriesCommand.STATUS_SUCCESS, status)
        expected_mean = control_chart.mean()
        actual_mean = self._analyze_series_cmd._control_chart.mean()
        self.assertAlmostEquals(expected_mean, actual_mean, places=3)

def suite():
    test_suite = unittest.TestSuite()

    for test_class in [ControlChartTest, AnalyzeSeriesCommandTest]:
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_class))

    return test_suite

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))