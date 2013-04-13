from pandas import *

class ControlChart:
    def __init__(self, data):
        self.dataFrame = DataFrame(data)

    def mean(self):
        return self.dataFrame.mean()

    def median(self):
        return self.dataFrame.median()

    def std_dev(self):
        return self.dataFrame.std()

    def points_outside_lcl(self):
        lcl = self.lower_control_limit()

        enumerated_values = enumerate(self.dataFrame.values)
        return [enumerated_value for enumerated_value in enumerated_values if enumerated_value[1] < lcl]

    def points_outside_ucl(self):
        ucl = self.upper_control_limit()

        enumerated_values = enumerate(self.dataFrame.values)
        return [enumerated_value for enumerated_value in enumerated_values if enumerated_value[1] > ucl]

    def upper_control_limit(self):
        return self.mean() + (3 * self.std_dev())

    def lower_control_limit(self):
        return self.mean() - (3 * self.std_dev())

    def control_limits(self):
        return (self.lower_control_limit(), self.upper_control_limit())

