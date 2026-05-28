#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# TODO
# Add functions to common:
#   lily_lyrics
# Lyrics
# Note groupings
# Slur options
# 1. Simple (all notes per syllable)
# 2. Simple parse (explicit breaks, punctum inclinatum)
# 3. Complex parse (detect Gregorio shapes)
# 4. Manual parse (colSlur)
# 5. St. Gall neumes
# 6. Laon neumes

import sys, os, re, argparse, getopt, io, csv
import pandas as pd
import common
from pprint import pprint

parser = argparse.ArgumentParser(description="option, GABC file",
  formatter_class=argparse.ArgumentDefaultsHelpFormatter)

#parser.add_argument("-no", "--suppress_gabc", action="store_true", help="Don't include GABC")
#parser.add_argument("-sg", "--include_stgall", action="store_true", help="Include St. Gall")
#parser.add_argument("-l", "--include_laon", action="store_true", help="Include Laon")

parser.add_argument("-s", "--slurs", default="w", help="Slur option: m: Manual, w: Whole syllable (default), s: Simple parse, c: Complex parse, g: St. Gall neumes, l:Laon neumes.")

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
output_format = "ly"

slur_option = localargs.slurs

#Files
input_file = args.input_file

if args.output_file is None:
  output_file = input_file
  output_file = re.sub(input_format + "$", output_format, output_file)
else:
  output_file = args.output_file

template = "template_226.ly"

#Variables

#############
#START HERE:#
#############

# Read in CSV
input_data = open(input_file, "r")
contents = csv.reader(input_data, delimiter='\t')
csv_table = []
for line in contents:
  csv_table.append(line)

# Lilypond notes
lilychant = common.lily_melody(csv_table, slur_option)
lilylyrics = common.lily_lyrics(csv_table, slur_option)

#print(lilychant, lilylyrics)

# Output Lilypond
lily_out = open(output_file, "w")
with open(template, "r") as template_file:
  contents = template_file.read()
template_file.close()

lily_contents = contents.replace("CHANT_MELODY", lilychant)
lily_contents = lily_contents.replace("LYRICS", lilylyrics)

lily_out = open(output_file, "w")
lily_out.write(lily_contents)
lily_out.close()

