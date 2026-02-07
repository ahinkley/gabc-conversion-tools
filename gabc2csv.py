#!/usr/bin/python3
# -*- coding: UTF-8 -*-

#This file creates the CSV
#The next converts it to Lilypond

#TODO
#IMPLEMENTED TO LINE:  59
#TODO CURRENT
#Implement read
#
#TODO
#Convert gabc etc to MIDI then Midi to Ly/Humdrum etc
#Need functions for each
#TODO add options for specifying key signature, specifying starting note
#TODO
#Consider moving all functions to chantfunctions.py
#then use import chantfunctions
#or import fromgabc, togabc
#
# -t transpose note new_note: add to semitones
# eg -tf c -tf d -ts 2 transposes c to d then adds an additional two semitones
# -s number of sharps
# -ts transpose number of semitones
# page reference
# 
#Open GABC to extract metadata: Filename, office part, etc
#If number of semitones selected:

import sys, os, re, argparse, getopt, io, csv

#option_default     ("-d", "--default", action="store_true", help="Default")

#Parameters
parser = argparse.ArgumentParser(description="option, GABC file",
  formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-d", "--default", action="store_true", help="Default")
parser.add_argument("-f", "--input_file", help="Input file")
parser.add_argument("-o", "--output_file", help="Output file")

#TODO add "starting note" as option.
parser.add_argument("-t", "--transpose_notes", nargs=2, help="Transpose from note (from, to)")
parser.add_argument("-ts", "--transpose_semitones", type=int, default=0, help="Transpose n semitones up")
parser.add_argument("-s", "--number_sharps", type=int, help="Number of sharps (negative for flats)")
parser.add_argument("-p", "--page_reference", help="Page reference")

args, unknown = parser.parse_known_args()
config = vars(args)

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
transpose_values = { "c":0, "ces":-1, "cis":1, "d":2, "des":1, "dis":3, "e":4, "ees":3, "eis":5, "f":5, "fes":4, "fis":6, "g":7, "ges":6, "gis":8, "a":9, "aes":8, "ais":10, "b":11, "bes":10, "bis":12 }

#Page reference
page_ref = args.page_reference

#Get number of semitones to transpose (key_transpose)
# sharps: Specify number of sharps in output
# semitone_adjust: Additional semitones to adjust
# key_transpose: transpose from one note to another
#Sharps is currently expressly specified, independent of transpose
semitone_adjust = int(args.transpose_semitones)
if args.number_sharps is not None:
  sharps = args.number_sharps
  if int(sharps) > 0:
    key_transpose = 7*int(sharps) % 12 + semitone_adjust
  else:
    key_transpose = 7*int(sharps) % 12 + semitone_adjust - 12
else:
  sharps = 0

if args.transpose_notes is not None:
  transpose_to_note = args.transpose_notes[1]
  transpose_from_note = args.transpose_notes[0]
  semitone_difference = transpose_values[transpose_to_note] - transpose_values[transpose_from_note]
  key_transpose = semitone_difference + semitone_adjust
#  if args.number_sharps is None:
#    if key_transpose >= 0:
#      sharps = (0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5)[key_transpose]
#    else:
#      #sharps = (0, 5, 10, 3, 8, 1, 6, 11, 4, 9, 2, 7)[key_transpose]
#      sharps = -1 * (0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5)[key_transpose]
else:
  key_transpose = semitone_adjust
#  if args.number_sharps is None:
#    if key_transpose >= 0:
#      sharps = (0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5)[key_transpose]
#    else:
#      #sharps = (0, 5, 10, 3, 8, 1, 6, 11, 4, 9, 2, 7)[key_transpose]
#      sharps = -1 * (0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5)[key_transpose]
#TODO need proper way to determine number of sharps if sharps not specified
# use sharps = true/false, specify flats if sharps == false
#Alternatively, use flats if sharps is 0 or negative

#if args.number_sharps is None:
#  if semitone_adjust >= 0:
#    sharps = (0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5)[key_transpose]
#  else:
#    sharps = (0, 5, 10, 3, 8, 1, 6, 11, 4, 9, 2, 7)[key_transpose]

#Note values
gabcnotes = ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m","n", "o", "p", "q", "r", "s", "t")
gabcnotes_caps = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M")
clef_adjust = {"c4":0, "c3":2, "c2":4, "c1":6, "f4":3, "f3":5, "f2":0, "f1":2}
gabcvalues = {"a":45, "b":47, "c":48, "d":50, "e":52, "f":53, "g":55, "h":57, "i":59, "j":60, "k":62, "l":64, "m":65, "n":67, "o":69, "p":71, "q":72, "r":74, "s":76, "t":77}

clef = "c3" #Default for Gregorio
flat = ''
#csv_title = ''
#csv_mode = ''
#csv_genre = ''

#Key signature variables
lastnote = ''
lastmidi = 60
mode = {0:"major", 2:"dorian", 4:"phrygian", 5:"lydian", 7:"mixolydian", 9:"minor", 11:"locrian"}

###########
#Functions#
###########

def read_gabc(gabc_filename) -> str:
  #Metadata
  gabc_data = {
    "gabcfile": "",
    "metadata": 1,
    "scorename": "",
    "officepart": "",
    "commentary": "",
    "mode": "",
    "annotation1": "",
    "annotation2": "",
    "gabc_code": ""
    }

  #Read GABC input
  #TODO Convert this to function read_gabc()
  gabcfile = open(gabc_filename,'r')
  contents = gabcfile.readlines()
  gabcfile.close()
  
  gabc_code = ''
  for line in contents:
    if gabc_data["metadata"] == 1:
      if re.match("^name", line):
        scorename = line
        scorename = re.sub('^[^:]*:','', scorename)
        scorename = re.sub(';[^;]*$','', scorename)
        gabc_data["scorename"] = scorename
      if re.match("^office-part", line):
        officepart = line
        officepart = re.sub('^[^:]*:','', officepart)
        officepart = re.sub(';[^;]*$','', officepart)
        gabc_data["officepart"] = officepart
      if re.match("^commentary", line):
        commentary = line
        commentary = re.sub('^[^:]*:','', commentary)
        commentary = re.sub(';[^;]*$','', commentary)
        gabc_data["commentary"] = commentary
      if re.match("^mode", line):
        mode = line
        mode = re.sub('^[^:]*:','', mode)
        mode = re.sub(';[^;]*$','', mode)
        gabc_data["mode"] = mode
      if re.match("^annotation",line):
        if gabc_data["annotation1"] is not None:
          annotation1 = line
          annotation1 = re.sub('^[^:]*:','', annotation1)
          annotation1 = re.sub(';[^;]*$','', annotation1)
          gabc_data["annotation1"] = annotation1
        else:
          annotation2 = line
          annotation2 = re.sub('^[^:]*:','', annotation2)
          annotation2 = re.sub(';[^;]*$','', annotation2)
          gabc_data["annotation2"] = annotation2
  #     = line
  #     = re.sub('^[^:]*:','', )
  #     = re.sub(';[^;]*$','', )
      if re.match("^%%", line):
        gabc_data["metadata"] = 0
    else:
      gabc_code = gabc_code + line
  gabc_data["gabc_code"] = gabc_code
  return gabc_data

#Convert gabc code to array of lyrics, individual notes, durations
def gabc2table(gabc: str) -> list:
  #Separate out Lyrics, GABC, NABC
  gabc_data = ""
  gabc_table = []
  gabc_table_long = []
 
  gabc_data = gabc.replace('\n', '')
  gabc_data = gabc_data.split(")")
  for i in range(len(gabc_data)):
    j = gabc_data[i]
    gabc_table.append(re.split(r"[(\|]", j))
 
  for i in range(len(gabc_table)):
    j = gabc_table[i]
    if len(j) <= 3:
      gabc_table_long.append(j)
    else:
      gabc_table_long.append(j[0:2])
      del j[:3]
      while True:
        if len(j) > 2:
          j.insert(0, '')
          gabc_table_long.append(j[:2])
          del j[:3]
        else:
          j.insert(0, '')
          gabc_table_long.append(j)
          break
  return gabc_table_long
#TODO print starting and ending notes

#TODO Turn flat on (flat = True) if x in GABC, keep flat on until end of word. (Detect new word if syllable[0] = " ")
def gabcnote2midi(gabcnote, clef, key_transpose, flat) -> int:
  gabcnotes = ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t")
#  gabcnotes_caps = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M")
  clef_adjust = {"c4":0, "c3":2, "c2":4, "c1":6, "f4":3, "f3":5, "f2":0, "f1":2}
  gabcvalues = {"a":45, "b":47, "c":48, "d":50, "e":52, "f":53, "g":55, "h":57, "i":59, "j":60, "k":62, "l":64, "m":65, "n":67, "o":69, "p":71, "q":72, "r":74, "s":76, "t":77}

  #Ensure lower case
  note = gabcnote[0].lower()
  midi_value = gabcvalues[note] + clef_adjust[clef]

  if "x" in gabcnote:
    midi_value = midi_value - 1

  return midi_value + key_transpose

def midi2ly(midivalue, sharps):
  midivalue = int(midivalue)
#  if value % 12 == flat:
#    value -= 1
  octave = int(midivalue / 12) - 1
  note = int(midivalue % 12)
  if sharps > 0:
    lilynote = ('c', 'cis', 'd', 'dis', 'e', 'f', 'fis', 'g', 'gis', 'a', 'ais', 'b')[note]
  else:
    lilynote = ('c', 'des', 'd', 'ees', 'e', 'f', 'ges', 'g', 'aes', 'a', 'bes', 'b')[note]
  lilynote += (",, ", ", ", "", "'", "''", "'''", "''''")[octave - 1]
  return lilynote



#Read array: 
#for each column
#  determine if voice or notes from code (eg S1L is Soprano lyrics, B2N is 2nd Bass notes)
#  read column and durations in parallel

#############
#START HERE:#
#############

#Read and parse GABC
data = read_gabc(input_file)
gabcdata = data["gabc_code"]
gabctable_short = gabc2table(gabcdata)

lycsv_table = [['Syllable', 'GABC', 'Duration', '.ly Note']]
#TODO Create modified version of this script for NOH
#With nohtable = ["Syllable", "GABC", "Multiplier", "Slur", "S", "A", "T", "B", "0 Sharps", "Key = g \mixolydian", "Ad te levavi", "Introit", "VIII.", "Gregorio clef: c4", "transposed 12 semitones", "Pageref pp: i.3"]
#With nohtable = ["Syllable", "GABC", "Multiplier", "Slur", "S", "A", "T", "B", number_sharps + " Sharps", "Key = g \mixolydian", "Ad te levavi", "Introit", "VIII.", "Gregorio clef: c4", "transposed 12 semitones", "Pageref pp: i.3"]
#output_csv.write("Syllable\tGABC\tMultiplier\tSlur\tS\tA\tT\tB\t" + str(sharps) + " Sharps, Key = \t" + str(lastnote) + " \\" + str(key_mode) + "\t" + str(ly_title) + "\t" + str(ly_genre) + "\t" +  str(ly_mode) + "\t" + "Gregorio clef: " + str(clef) + ", transposed " + str(semitone_adjust % 12) + "(" + str((semitone_adjust % 12) - 12) + ")" + " semitones. Pageref pp:\tii." + str(page_ref) + "\n")

#Expand table
for row in gabctable_short:
  if len(row) < 2:
    continue
  temp = row[1]
  #repeat notes vvv, sss:
  temp = re.sub(r"([a-m])vvv", r"\1v\1v\1v", temp)
  temp = re.sub(r"([a-m])sss", r"\1s\1s\1s", temp)
  temp = re.sub(r"([a-m])vv", r"\1v\1v", temp)
  temp = re.sub(r"([a-m])ss", r"\1s\1s", temp)
  #Split into individual notes plus effects
  temp = re.sub(r"([a-m])", r"<>\1", temp)
  temp = re.split("<>", temp)
  #Remove empty elements
  temp = list(filter(None, temp))

  #TODO If x in note, set flat to true until end of word
  #TODO If y in note, set flat to false

  lycsv_table.append([row[0],temp[0]])
  for item in temp[1:]:
    lycsv_table.append(['',item])

#Add midi values TODO replace midi values with Lily values
clef = "c3" #default value
for index in range(len(lycsv_table)):
  current_gabc_note = lycsv_table[index][1]
  duration = 1
  #Turn off flat at word boundary
  if lycsv_table[index][0][0] == " ":
      flat = False
  if re.match(r"[a-mA-M]", current_gabc_note[0]):
    if "x" in current_gabc_note:
      flat = True
    if "y" in current_gabc_note:
      flat = False
    if "." in current_gabc_note:
      duration = 1.5
    if re.match(r"[cf][1-4]", current_gabc_note):
      clef = current_gabc_note[0:2]
      duration = 0
  if re.match(r'[,;:]', current_gabc_note):
    duration = 0
  if duration != 0:
    current_midi_note = gabcnote2midi(current_gabc_note, clef, key_transpose)
    current_lily_note = midi2ly(current_midi_note, sharps)
  else:
    current_midi_note = ''
    current_lily_note = ''
  lycsv_table[index] += [duration, current_midi_note, current_lily_note]
for row in range(len(lycsv_table)):
  print(lycsv_table[row])


#Convert GABC notes in column[1] to Lilypond via gabc2midi


#if only one element, add ''
#TODO
#    if sss or vvv in note, split into three notes  
#  Go through table:
#    if "." in notes[i] then duration = 1.5
#    if sss
#
#    Syllable    GABC    Multiplier  Slur    S   A   T   B   0 Sharps, Key =     g \mixolydian   Ad te levavi    Introit VIII.   Gregorio clef: c4, transposed 12 semitones. Pageref pp: i.3

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

print(midi2ly(61,1))
