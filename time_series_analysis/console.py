#!/usr/bin/env python
import sys

from tools import AnalyzeSeriesCommand

def main():
    analyze_series_command = AnalyzeSeriesCommand()

    (status, message) = analyze_series_command.execute()
    if status > 0 and message:
        sys.stderr.write("stderr: {}\n".format(message))
    sys.exit(status)