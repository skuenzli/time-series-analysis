#!/usr/bin/env python

from random import choice
import sys
import unittest
import tempfile
from mock import MagicMock
import xmlrunner

from time_series_analysis.tools import ControlChart, AnalyzeSeriesCommand

SERIES_UNDER_CONTROL = (10.0, 9.0, 8.5, 11.5, 10.25, 9.75, 10.1, 9.9, 11, 10.5)

SERIES_WITH_UCL_OUTLIERS = (-1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1,
                            4,
                            -1, 0, 1, -1, 0, 1, -1, 0, 1)

SERIES_WITH_LCL_OUTLIERS = (-4,
                            -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1)

SERIES_WITH_LAST_POINT_OOC = (-1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1,
                              4)


def random_bool():
    return choice([True, False])


class ControlChartTest(unittest.TestCase):

    # calculated values sourced from wolfram alpha

    def setUp(self):
        pass

    def test_series_under_control(self):
        chart = ControlChart(SERIES_UNDER_CONTROL)

        self.assertEquals(10.05, chart.mean())
        self.assertEquals(10.05, chart.median())
        self.assertAlmostEquals(0.8737, chart.std_dev(), places=4)

        self.assertAlmostEquals(7.429, chart.lower_control_limit(), places=3)
        self.assertAlmostEquals(12.671, chart.upper_control_limit(), places=3)

        self.assertEquals([], chart.points_outside_lcl())
        self.assertEquals([], chart.points_outside_ucl())

    def test_points_outside_lcl_are_identified(self):
        chart = ControlChart(SERIES_WITH_LCL_OUTLIERS)

        index = 0
        value = -4
        self.assertIn((index, value), chart.points_outside_lcl())

    def test_points_outside_ucl_are_identified(self):
        chart = ControlChart(SERIES_WITH_UCL_OUTLIERS)

        index = 18
        value = 4
        self.assertIn((index, value), chart.points_outside_ucl())

    def test_get_last_point(self):
        chart = ControlChart(SERIES_UNDER_CONTROL)

        last_index = len(SERIES_UNDER_CONTROL) - 1
        expected_last_point = (last_index, SERIES_UNDER_CONTROL[last_index])

        last_point = chart.get_last_point()
        print "expected_last_point: {}".format(expected_last_point)
        print "last_point: {}".format(last_point)
        self.assertEquals(expected_last_point, last_point)

    def test_chart_handles_get_last_point_on_empty_series_gracefully(self):
        series = ()
        chart = ControlChart(series)

        self.assertIsNone(chart.get_last_point())

    def test_chart_can_get_last_point_when_only_one_point_exists(self):
        series = (42,)
        chart = ControlChart(series)

        self.assertEquals((0, 42), chart.get_last_point())

    def test_is_last_point_in_control_does_not_generate_false_positives_when_outliers_exist_but_are_not_last(self):
        chart = ControlChart(SERIES_WITH_UCL_OUTLIERS)

        chart_points_outside_ucl = chart.points_outside_ucl()
        self.assertGreater(len(chart_points_outside_ucl), 0)
        self.assertTrue(chart.is_last_point_in_control())

    def test_chart_computes_sample_statistics(self):
        series = (1, 2, 2, 3, 3, 3, 2, 2, 1)
        chart = ControlChart(series)

        self.assertAlmostEqual(2.1111, chart.mean(), places=4)
        self.assertEquals(2, chart.median())
        self.assertAlmostEqual(0.78173, chart.std_dev(), places=3)
        self.assertEquals(len(series), chart.count())

    def test_chart_computes_control_limits(self):
        chart = ControlChart(SERIES_WITH_UCL_OUTLIERS)

        (lcl, ucl) = chart.control_limits()

        self.assertEquals(lcl, chart.lower_control_limit())
        self.assertEquals(ucl, chart.upper_control_limit())

        self.assertAlmostEqual(lcl, -3.1952, places=4)
        self.assertAlmostEqual(ucl, 3.4809, places=4)

class AnalyzeSeriesCommandTest(unittest.TestCase):

    def setUp(self):
        self._analyze_series_cmd = AnalyzeSeriesCommand()

    def test_properties_when_no_arguments_provided(self):
        sys.argv = ["analyze_series"]
        cmd = AnalyzeSeriesCommand()

        self.assertIsNotNone(cmd._argument_parser)
        cmd._parse_options()

        self.assertEquals(sys.stdin, cmd._input_file)
        self.assertFalse(cmd._verbose)

    def test_properties_when_arguments_provided(self):
        tf = tempfile.NamedTemporaryFile(mode="r")

        sys.argv = ["analyze_series", tf.name]

        verbosity = random_bool()
        if verbosity:
            sys.argv.append("--verbose")

        assert_last_point_in_control = random_bool()
        if assert_last_point_in_control:
            sys.argv.append("--assert-last-point-in-control")

        cmd = AnalyzeSeriesCommand()

        cmd._parse_options()

        self.assertEquals(tf.name, cmd._input_file.name)
        self.assertEquals(verbosity, cmd._verbose)
        self.assertEquals(assert_last_point_in_control, cmd._assert_last_point_in_control)

    def test_parseOptions_called_when_executed(self):
        mock_parse_options = MagicMock()
        self._analyze_series_cmd._parse_options = mock_parse_options

        self._analyze_series_cmd.execute()

        mock_parse_options.assert_called_once_with()

    def test_data_series_is_analyzed(self):
        tf = tempfile.NamedTemporaryFile()
        control_chart = ControlChart(SERIES_UNDER_CONTROL)

        test_input = ""
        for val in SERIES_UNDER_CONTROL:
            test_input += " {} \n".format(str(val))

        tf.write(test_input)
        tf.flush()

        sys.argv = ["analyze_series", tf.name, "--verbose"]

        (status, message) = self._analyze_series_cmd.execute()

        self.assertEquals(AnalyzeSeriesCommand.STATUS_SUCCESS, status)
        self.assertEquals("", message)

        expected_mean = control_chart.mean()
        actual_mean = self._analyze_series_cmd._control_chart.mean()
        self.assertAlmostEquals(expected_mean, actual_mean, places=3)

    def test_status_codes_are_reasonable(self):
        self.assertEquals(0, AnalyzeSeriesCommand.STATUS_SUCCESS)

        self.assertLess(0, AnalyzeSeriesCommand.STATUS_ASSERTION_FAILED)
        self.assertLess(0, AnalyzeSeriesCommand.STATUS_ERROR_IO)

    def test_exit_status_when_assert_last_point_in_control_not_set_and_out_of_control(self):
        self._analyze_series_cmd._read_data_from_file = MagicMock(return_value=SERIES_WITH_UCL_OUTLIERS)
        sys.argv = ["analyze_series"]

        (status, message) = self._analyze_series_cmd.execute()

        self.assertFalse(self._analyze_series_cmd._assert_last_point_in_control)
        self.assertEquals(AnalyzeSeriesCommand.STATUS_SUCCESS, status)
        self.assertEquals('', message)

    def test_exit_status_when_assert_last_point_in_control_is_set_and_non_last_point_out_of_control(self):
        self._analyze_series_cmd._read_data_from_file = MagicMock(return_value=SERIES_WITH_UCL_OUTLIERS)
        sys.argv = ["analyze_series", "--assert-last-point-in-control"]

        (status, message) = self._analyze_series_cmd.execute()

        self.assertTrue(self._analyze_series_cmd._assert_last_point_in_control)
        self.assertEquals(AnalyzeSeriesCommand.STATUS_SUCCESS, status)
        self.assertEquals('', message)

    def test_exit_status_when_assert_last_point_in_control_is_set_and_last_point_out_of_control(self):
        self._analyze_series_cmd._read_data_from_file = MagicMock(return_value=SERIES_WITH_LAST_POINT_OOC)
        sys.argv = ["analyze_series", "--assert-last-point-in-control"]

        (status, message) = self._analyze_series_cmd.execute()

        self.assertTrue(self._analyze_series_cmd._assert_last_point_in_control)
        self.assertEquals(AnalyzeSeriesCommand.STATUS_ASSERTION_FAILED, status)
        self.assertIsNotNone(message)


def suite():
    test_suite = unittest.TestSuite()

    for test_class in [ControlChartTest, AnalyzeSeriesCommandTest]:
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_class))

    return test_suite

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))