Time Series Analysis
====================
Contains tools for analyzing time-series data.

Command-Line Tools
------------------
The _analyze_series_ command is meant to be used in the command-line in typical *nix fashion, expecting:
* one number per line
* input on standard input or as a file argument to analyze_series

### Usage
analyze_series [-h] [-v] [input_file]

positional arguments:
  input_file     input file to process, defaults to standard input

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  print additional debug information

### Examples

Analyze a file on the filesystem:
````bash
$ ./analyze_series resources/examples/multiple_control_limit_violation.txt
median: 0.0
mean: 0.0357142857143
std dev: 1.41375432756
lower control limit: -4.20554869697
upper control limit: 4.2769772684
points outside of lcl: [(3, -5.0)]
points outside of ucl: [(28, 7.0)]
````

Analyze data arriving on standard input:
````bash
$ cat resources/examples/under_control.txt | ./analyze_series
median: 10.05
mean: 10.05
std dev: 0.873689494805
lower control limit: 7.42893151558
upper control limit: 12.6710684844
points outside of lcl: []
points outside of ucl: []
````