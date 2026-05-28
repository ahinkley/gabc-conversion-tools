#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# TODO
# Specify clef
# Clef should be specified in metadata

import sys, os, re, argparse, getopt, io, csv
import pandas as pd
import common
from pprint import pprint

parser = argparse.ArgumentParser(description="option, GABC file",
  formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-no", "--suppress_gabc", action="store_true", help="Don't include GABC")
parser.add_argument("-sg", "--include_stgall", action="store_true", help="Include St. Gall")
parser.add_argument("-l", "--include_laon", action="store_true", help="Include Laon")

localargs, unknown = parser.parse_known_args()
config = vars(localargs)


#Import variables
args = common.args
sharps = int(common.sharps)
key_transpose = common.key_transpose
headers = common.headers

##########################################
#Script specific variables and parameters#
##########################################
input_format = "csv"
output_format = "gabc"

gabc = localargs.suppress_gabc
stgall = localargs.include_stgall
laon = localargs.include_laon

#Files
input_file = args.input_file

if args.output_file is None:
  output_file = input_file
  output_file = re.sub(input_format + "$", output_format, output_file)
else:
  output_file = args.output_file

#Variables

#############
#START HERE:#
#############

# Read in CSV
input_data = open(input_file, "r")
contents = csv.reader(input_data,delimiter='\t')
csv_table = []
for line in contents:
  csv_table.append(line)

# Create GABC
#TODO How to handle St. Gall and Laon?
gabc_code = common.table2gabc(csv_table,gabc,stgall,laon)

# Output GABC
gabc_out = open(output_file, "w")
gabc_out.write(gabc_code)
gabc_out.close()

# (Optional) Compile GABC

