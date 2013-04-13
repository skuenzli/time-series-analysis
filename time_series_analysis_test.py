import unittest
import xmlrunner

from time_series_analysis import ControlChart

class ControlChartTest(unittest.TestCase):

    # calculated values sourced from wolfram alpha

    def setUp(self):
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


def suite():
    test_suite = unittest.TestSuite()

    for test_class in [ControlChartTest]:
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_class))

    return test_suite

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))