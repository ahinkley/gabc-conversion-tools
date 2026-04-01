#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# TODO
# CSV format accepts LilyNote and Syllable for one voice
# Accepted fields will include name, office-part, transpose, key, sharps, reference,



import sys, os, re, argparse, getopt, io, csv
import pandas as pd
import common
from pprint import pprint

#Import variables
args = common.args
sharps = int(common.sharps)
key_transpose = common.key_transpose
headers = common.headers

##########################################
#Script specific variables and parameters#
##########################################
input_format = "gabc"
output_format = "csv"

#Files
input_file = args.input_file

if args.output_file is None:
  output_file = input_file
  output_file = re.sub(input_format + "$", output_format, output_file)
else:
  output_file = args.output_file

#Variables

#Page reference
page_ref = args.page_reference

#############
#START HERE:#
#############

#Read and parse GABC
data = common.read_gabc(input_file)
gabcdata = data['gabc_code']

#Create main table
lycsv_table = common.gabc2table(gabcdata)

#Add GABC note shapes
lycsv_table = common.gabcnoteshapes(lycsv_table)

#Add GABC Neumes
lycsv_table = common.neumeshapes(lycsv_table)

#Add MIDI values
lycsv_table = common.gabc2midi_table(lycsv_table)
#TODO a space in the notes breaks the function

#Add Lily Values
lycsv_table = common.midi2ly_table(lycsv_table)

#Write file
##TODO Temporary
#with open("test2.csv", 'w', newline='') as testfile:
#    headers = ["Syllable", "Current_gabc_note", "Neume", "Value", "Joinable", "Slur"]
#    csv_writer = csv.writer(testfile, delimiter='\t')
#    csv_writer.writerow(headers)
##TODO need nt
#    #csv_writer.writerows(nt)
#testfile.close()

#
#Write file
#for row in range(len(lycsv_table)):
#  print(lycsv_table[row])
with open(output_file, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter='\t')
    csv_writer.writerows(lycsv_table)

print("Input file is: " + input_file)
print("Output file is: " + output_file)
#if args.number_sharps is not None:
if sharps >= 0:
  print("Key signature has " + str(sharps) + " sharps")
else:
  print("Key signature has " + str(abs(sharps)) + " flats.")
if key_transpose >= 0:
  print ("Adjusted up " + str(key_transpose) + " semitones.")
else:
  print ("Adjusted down " + str(abs(key_transpose)) + " semitones.")


#for index in range(1,len(nt)):
# print(neume_table[index])

csvfile.close()
#print(nt)
