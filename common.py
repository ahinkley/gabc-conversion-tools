#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys, os, re, argparse, getopt, io, csv

# TODO
# IMPLEMENTED TO LINE:  59
# TODO CURRENT
# Implement read
#
#TODO For direct conversions eg GABC to Lily
# Create CSV internally but do not write to file
# Or write file for corrections to be made
# Or write file anyway
#
#TODO
#Logic for converting neumes to neumeshapes
#Logic for converting Meinrad to neumeshapes
#TODO
#Add option to specify number of NABC lines and specify StG/Laon
#Add option for NABC only (eg for transcribing E121)
#Add logic to detect StG or Laon if unspecified (or error message)
# TODO Finish transpose options
# TODO Add mode calculation to metadata
# TODO Replace "sharps" with "key signature"
# TODO How to add linebreaks?

# TODO
# Add function: Fill column, eg fill_col(Meinrad, gabc) adds meinrad encodings from gabc
#
# TODO Add code from meinrad2gabc
#
# TODO
#  -sn starting note
# TODO add "starting note" as option.
#  -tk transpose to key
#  -t transpose note new_note: add to semitones
#  eg -tf c -tf d -ts 2 transposes c to d then adds an additional two semitones
#  -s number of sharps
#  -ts transpose number of semitones
#  page reference
# 
# TODO
# src/gabc/gabc-glyphs-determination.c
# for determining which glyphs are joined
# Use this to determine which notes to join in slurs.

# option_default     ("-d", "--default", action="store_true", help="Default")
# TODO GABC should have an argument for clef. Mode can be specified or calculated
# TODO -f and -t options can be calculated from extension if options not specified

# TODO Can Meinrad be integrated into this?
# Output GABC table with guessed syllables
# TODO Integrate gabc2csv into here
# Use csv.Dictreader, csv.Dictwriter for indexing columns
# TODO Add columns for Humdrum, Meinrad raw, Meinrad values, ABC, Verovio
# Consider filling out all columns in script.
# Output file eg ad_te_levavi.csv then fill in columns with different scripts
# Will need to distinguish between ChantCSV, PolyCSV, OrganCSV
#TODO CSV to Meinrad and CSV to Caecilia exports to RTF or DOCX?

# TODO conversion chart: Mark X when completed (Input on side, out on top)
#      To: g h c l a v    gregorio, humdrum, csv, lilypond, abc, verovio
# From
#   g      X      
#   h        X    
#   c          X   
#   l            X 
#   a              X
#   v                X
# TODO
# Add chord to Lily if "}" in colGABC
# TODO 
# Perhaps rename "gabc_extended_table" in function(gabc_extended_table) to avoid inconsistency
# use function(gabc_full_table) instead.



#Parameters
parser = argparse.ArgumentParser(description="option, GABC file",
  formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-d", "--default", action="store_true", help="Default")
parser.add_argument("-f", "--input_file", help="Input file")
parser.add_argument("-o", "--output_file", help="Output file")

parser.add_argument("-if", "--input_format", type=str, help="Input file")
parser.add_argument("-of", "--output_format", help="Output file")

parser.add_argument("-t", "--transpose_notes", nargs=2, help="Transpose from note (from, to)")
parser.add_argument("-ts", "--transpose_semitones", default=0, type=int, help="Transpose n semitones up")
#parser.add_argument("-s", "--number_sharps", help="Number of sharps (negative for flats)")
parser.add_argument("-ks", "--key_signature", help="Number of sharps (negative for flats)")
parser.add_argument("-p", "--page_reference", help="Page reference")



# TODO add nargs="?" for optional 0 or 1 arguments?
# Consider nested arguments, eg --clef for --to_gabc, eg -tg -cl c3
# GABC needs argument "clef", Lilypond needs argument for key or number of sharps
parser.add_argument("-fg", "--from_gabc", action="store_true", help="Input file is GABC")
#parser.add_argument("-fh", "--from_humdrum", action="store_true", help="Input file is Humdrum")
#parser.add_argument("-fc", "--from_csv", action="store_true", help="Input file is CSV")
#parser.add_argument("-fl", "--from_lilypond", action="store_true", help="Input file is Lilypond")
#parser.add_argument("-fa", "--from_abc", action="store_true", help="Input file is ABC")
#parser.add_argument("-fv", "--from_verovio", action="store_true", help="Input file is Verovio")

#parser.add_argument("-tg", "--to_gabc", action="store_true", help="Output file is ")
#parser.add_argument("-th", "--to_humdrum", action="store_true", help="Output file is ")
#parser.add_argument("-tc", "--to_csv", action="store_true", help="Output file is ")
#parser.add_argument("-tl", "--to_lilypond", action="store_true", help="Output file is Lilypond")
#parser.add_argument("-ta", "--to_", action="store_true", help="Output file is ABC")
#parser.add_argument("-tv", "--to_", action="store_true", help="Output file is Verovio")

#Context specific options
parser.add_argument("-cl", "--gabc_clef", default="c4", help="GABC clef")



args, unknown = parser.parse_known_args()
config = vars(args)


#Files

#File extensions
file_extensions = {
  "gabc": "gregorio",
  "ly": "lilypond",
  "csv": "csv",
  "krn": "humdrum",
  "abc": "abc"
#  "": "verovio"
}

if args.input_format is None:
  input_file = args.input_file
  input_format = input_file
  input_format = re.sub(r".*\.", "", input_format)

if args.output_format is None:
  try:
    output_file = args.output_file
    output_format = output_file
    output_format = re.sub(r".*\.", "", output_format)
  except:
    print("Error: Please specify output file or format")
else:  
  output_format = args.output_format

###########
#Variables#
###########

#CSV/table headers
headers = ['Index', 'Syllable', 'Translation', 'GABC', 'St. Gall', 'Laon', 'Neume', 'Neume shape', 'Duration', 'MIDI value', 'LilyNote', 'Slur', 'Linebreak', 'Meinrad', 'Caecilia', 'ABC', 'Humdrum', 'Volpiano', 'Metadata headers', 'Metadata values']

# Index values:
colIndex = 0
colSyllable = 1
colTranslation = 2
colGABC = 3
colSt_Gall = 4
colLaon = 5
colNeume = 6
colNeumeshape = 7
colDuration = 8
colMIDI_value = 9
colLilyNote = 10
colSlur = 11
colLinebreak = 12
colMeinrad = 13
colCaecilia = 14
colABC = 15
colHumdrum = 16
colVolpiano = 17
colMetaHeaders = 18
colMetaValues = 19
numCols = 20

# Notes
gabcnotes = ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m","n", "o", "p", "q", "r", "s", "t")
gabcnotes_caps = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M")
clef_adjust = {"c4":0, "c3":2, "c2":4, "c1":6, "f4":3, "f3":5, "f2":0, "f1":2}
gabcvalues = {"a":45, "b":47, "c":48, "d":50, "e":52, "f":53, "g":55, "h":57, "i":59, "j":60, "k":62, "l":64, "m":65, "n":67, "o":69, "p":71, "q":72, "r":74, "s":76, "t":77}

clef = "c3" # Default for Gregorio
flat = ''
ly_title = ''
ly_mode = ''
ly_genre = ''

# Key signature variables
lastnote = ''
lastmidi = 60
mode = {0:"major", 2:"dorian", 4:"phrygian", 5:"lydian", 7:"mixolydian", 9:"minor", 11:"locrian"}
# TODO
# Calculate key signature from last colLilyNote where note[0] in [a-g]
# Start at index -1 and count backwards

# Transpose

# TODO Types of transpose
# 1. Specify number of sharps (ks)
# 2. From note to note (transpose_notes) (t n1 n2)
# 3. Choose key (k key/mode)
# 4. Transpose n semitones (semitone_adjust) 
# 5. Choose first note (sn start-note)
# 6. Choose last note (fn final-note)
#
# Return: key_transpose
# Compatible options: 1,4
# Non-compatible options: 5

#TODO Convert this to a function semitone_adjust = transpose(ks, t1, t2, etc)
key_transpose = 0
transpose_values = { "c":0, "ces":-1, "cis":1, "d":2, "des":1, "dis":3, "e":4, "ees":3, "eis":5, "f":5, "fes":4, "fis":6, "g":7, "ges":6, "gis":8, "a":9, "aes":8, "ais":10, "b":11, "bes":10, "bis":12 }

# 4. Semitone adjust
if args.transpose_semitones is None:
  semitone_adjust = 0
else:
  semitone_adjust = int(args.transpose_semitones)
key_transpose += semitone_adjust

# 1. Number of sharps
if args.key_signature is not None:
  sharps = args.key_signature
  if int(sharps) > 0:
    key_transpose = 7*int(sharps) % 12 + semitone_adjust
  else:
    key_transpose = 7*int(sharps) % 12 + semitone_adjust - 12
else:
  sharps = 0

# 2 Transpose notes
if args.transpose_notes is not None:
  transpose_to_note = args.transpose_notes[1]
  transpose_from_note = args.transpose_notes[0]
  semitone_difference = transpose_values[transpose_to_note] - transpose_values[transpose_from_note]
  key_transpose += semitone_difference

# 3 TODO
#Function read table[lynote], find semitone difference, adjust



# 5 TODO
#Function read table[lynote], find semitone difference, adjust

# 6 TODO
#Function read table[lynote], find semitone difference, adjust


#Page reference
page_ref = args.page_reference

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

################
#GABC functions#
################

#Import and parse the GABC file
def read_gabc(gabc_filename):
  #Metadata
  gabc_data = {
    "gabcfile": gabc_filename,
    "gabc_code": ""
    }

  #Read GABC input
  gabcfile = open(gabc_filename,'r')
  contents = gabcfile.readlines()
  gabcfile.close()
  
  metadata = True
  gabc_code = ''
  for line in contents:
    if metadata == True:
      if re.match("^%%", line):
        metadata = False
      else:
        row = line
        row = re.sub(r"\n", "", row)
        name = re.sub(r"^([^:]*):(.*);$", r"\1", row)
        val = re.sub(r"^([^:]*):(.*);$", r"\2", row)
        
        # Allow for two annotation fields
        if name == "annotation" and "annotation" in gabc_data:
          name = "annotation2"

        gabc_data[name] = val
    else:
      gabc_code = gabc_code + line
  gabc_data["gabc_code"] = gabc_code

  return gabc_data

#def gabc2table(gabc: str) -> list:
def gabc2table(gabc_meta):
  # Separate out Lyrics, GABC, NABC
  # gabc_data: Separate syllables. 
  # gabc_table: Split syllables into one row per syllable.
  # gabc_table_long: Separate out NABC.
  # gabc_table_extended: Split GABC into one row per note.
  # gabc_full_table: Extra columns added
  gabc_data = ""
  gabc_table = []
  gabc_table_long = []
  gabc_table_extended = []

  gabc_data = gabc_meta["gabc_code"]
  gabc_data = gabc_data.replace('\n', '')

  # Workaround to handle brackets in translation
  brackets = {
    "<v>[</v>": "XLSB",
    "<v>]</v>": "XRSB",
    "<v>(</v>": "XLB",
    "<v>)</v>": "XRB"
    }
  pattern = re.compile("|".join(re.escape(key) for key in brackets.keys()))
  gabc_data = pattern.sub(lambda match: brackets[match.group(0)], gabc_data)

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

  # Extend table
  for row in gabc_table_long:
    # Add NABC column if absent
    #TODO How to handle nabc-lines = 2?
    if len(row) < 3:
      row += [''] * (3 - len(row))

    temp = row[1]
    # repeat notes vvv, sss:
    temp = re.sub(r"([a-m])vvv", r"\1v\1v\1v", temp)
    temp = re.sub(r"([a-m])sss", r"\1s\1s\1s", temp)
    temp = re.sub(r"([a-m])vv", r"\1v\1v", temp)
    temp = re.sub(r"([a-m])ss", r"\1s\1s", temp)
    # Split into individual notes plus effects
    temp = re.sub(r"([a-mA-Mz`,])", r"<>\1", temp)
    temp = re.sub(r"(:{1,2})", r"<>\1", temp)
    temp = re.split("<>", temp)
    # Remove empty elements
    temp = list(filter(None, temp))
  
    # TODO If x in note, set flat to true until end of word
    # TODO If y in note, set flat to false
    
  #TODO Add way to detect if St.Gall or Laon
  #TODO Add way to have both St. Gall and Laon
    if len(temp) >= 1:
      syl = row[0]
      tran = ''
      gabc = temp[0]
      sg = row[2]
      l = ''
      gabc_table_extended.append(['',syl,tran,gabc,sg,l])
    if len(temp) >= 2:
      for item in temp[1:]:
        syl = ''
        tran = ''
        gabc = item
        sg = ''
        l = ''
        gabc_table_extended.append(['',syl,tran,gabc,sg,l])
  # Return table with [Syllable, Translation, GABC, NABC (St. Gall), NABC (Laon)]
  
  # Create full table
  gabc_full_table = []
  gabc_full_table.append(headers)
  for row in gabc_table_extended:
    row += [''] * (numCols - len(row))
    gabc_full_table.append(row)

  # Add index
  for index in range(1,len(gabc_full_table)):
    gabc_full_table[index][0] = index

  # Separate lyrics and translations
  # TODO Need to add <v> tags for () and [] in translations
  for row in range(1,len(gabc_full_table)):
    syllable = gabc_full_table[row][colSyllable]
    if re.search("\[", syllable):
      syl = re.sub("\[.*\]", "", syllable)
      trn = re.sub(".*\[", "", syllable)
      trn = re.sub("\]", "", trn)

      # Reverse bracket substitutions
      reverse_brackets = {
        "XLSB": "[",
        "XRSB": "]",
        "XLB": "(",
        "XRB": ")"
      }
      reverse_pattern = re.compile("|".join(re.escape(key) for key in reverse_brackets.keys()))
      
      syl = reverse_pattern.sub(lambda match: reverse_brackets[match.group(0)], syl)
      trn = reverse_pattern.sub(lambda match: reverse_brackets[match.group(0)], trn)

      gabc_full_table[row][colSyllable] = syl
      gabc_full_table[row][colTranslation] = trn

  # Add metadata to table
  meta_index = 0
  for key in gabc_meta:
    meta_index += 1
    gabc_full_table[meta_index][colMetaHeaders] = key
    gabc_full_table[meta_index][colMetaValues] = gabc_meta[key]


  return gabc_full_table

#TODO print starting and ending notes

#TODO Turn flat on (flat = True) if x in GABC, keep flat on until end of word. (Detect new word if syllable[0] = " ")
def gabcnote2midi(gabcnote, clef, key_transpose, flat) -> int:
  gabcnotes = ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t")
  #clef_adjust = {"c4":0, "c3":2, "c2":4, "c1":6, "f4":3, "f3":5, "f2":0, "f1":2}
  clef_adjust = {"c4":0, "c3":2, "c2":4, "c1":6, "f4":-4, "f3":-2, "f2":0, "f1":2}
  gabcvalues = {"a":45, "b":47, "c":48, "d":50, "e":52, "f":53, "g":55, "h":57, "i":59, "j":60, "k":62, "l":64, "m":65, "n":67, "o":69, "p":71, "q":72, "r":74, "s":76, "t":77}

  #Ensure lower case
  note = gabcnote[0].lower()

  value = gabcnotes.index(note)
  clef_value = clef_adjust[clef]
  value += clef_value

  midi_value = gabcvalues[gabcnotes[value]]

  if note == flat:
    midi_value -= 1

  return midi_value + key_transpose

#TODO Move this to function fillMIDIfromGABC
#For row in lycsvtable: row[4] = gabctomidi(row[1])
# Add midi values TODO replace midi values with Lily values


# TODO Move this to common under function name gabcslurs and integrate with main GABC table (add columns rather than new table)
# TODO Add functions gabcslurs, gabcshapes
# Parse GABC (determine neume type)
# TODO figure out the logic in glyph-determination
# Neume break at "/" or end-of-syllable
# Initial determination:

def gabcnoteshapes(gabc_extended_table):
  table = gabc_extended_table
  for index in range(1,len(table)):
    syllable = table[index][colSyllable]
    current_gabc_note = table[index][colGABC]
    neume = ""
    joinable = 0
    note_break = 1
    #Initial type
    if re.search(r"[A-M]", current_gabc_note):
      neume = "pi" #punctum_inclinatum
    elif re.search("o", current_gabc_note):
      neume = "or" #oriscus
    elif re.search("w", current_gabc_note):
      neume = "qu" #quilisma
    elif re.search(r"[vV]", current_gabc_note):
      neume = "vi" #virga
    elif re.search("s", current_gabc_note):
      neume = "st" #stropha
    elif re.search("~", current_gabc_note):
      neume = "ld" #liquescent_deminutus
    elif re.search("<", current_gabc_note):
      neume = "al" #augmented liquescent
    elif re.search(">", current_gabc_note):
      neume = "dl" #diminished liquescent
    elif re.search("x", current_gabc_note):
      neume = "fl" #flat
    elif re.search("#", current_gabc_note):
      neume = "sh" #sharp
    elif re.search("y", current_gabc_note):
      neume = "na" #natural
    elif re.search(r"[`,;:]", current_gabc_note):
      neume = "di" #division
    elif re.search(r"[cf][1-4]", current_gabc_note):
      neume = "cf" #clef
    elif re.search(r"[zZ]", current_gabc_note):
      neume = "br" #linebreak
    else:
      if re.match(r"[a-m]", current_gabc_note):
        neume = "pu" #punctum
      else:
        neume = ""
    table[index][colNeume] = neume
  return table
#    # Joinable
#    joinable_neumes = ("pu", "or", "qu", "li", "al", "dm", "ld", "pi")
#    if neume in joinable_neumes:
#      joinable = 1
#  
#    if r'/' in current_gabc_note:
#      joinable = 0
#    try:
#      if table[index+1][0] != "":
#        joinable = 0
#    except:
#      joinable = 0
#    try:
#      if table[index][4] == table[index+1][4]:
#        joinable = 0
#    except:
#      joinable = 0
#
#  #TODO add logic for neume shapes porrectus, torculus, etc


  #neume_table.append([syllable, current_gabc_note, neume, value, joinable, slur])

#def lily_simple_slurs:
## Add slurs
#n = 0
#m = 1
## nt = pd.DataFrame(neume_table, columns=["Syllable", "Current_gabc_note", "Neume", "Value", "Joinable", "Slur"])
#nt = neume_table
#nt.append(["","","","","","",""])
#
##  syllable = nt[n][0]
##  current_gabc_note = nt[n][1]
##  neume = nt[n][2]
##  value = nt[n][3]
##  joinable = nt[n][4]
##
#while n < len(nt):
#  m = 1
#  if nt[n][2] in joinable_neumes:
#    while True:
#      if nt[n+m][2] in joinable_neumes:
#        nt[n+m][2] = ""
#        slur = m
#        if nt[n+m][4] == 1:
#          m = m+1
#        else:
#          if m > 0:
#            nt[n][5] = m + 1
#            nt[n][2] = "x" + str(m+1)
#          break
#      else:
#        if m > 1:
#          nt[n][2] = "x" + str(m)
#          nt[n][5] = m
#        break
#
#  if nt[n][2] == "vi":
##    if nt[n+1][2] == "vi":
##      neume = "bv"
##      nt[n+1][2] = ""
##      m = m+1
##      if nt[n+2][2] == "vi":
##        neume = "tv"
##        nt[n+2][2] = ""
##        m = m+1
#    m = 1
#    while True:
#      if nt[n+m][2] == "pi":
#        nt[n][2] = "cm" # Climacus plus
#        nt[n+m][2] = ""
#        slur = m
#        m = m+1
#      else:
#        if m > 1:
#          nt[n][5] = m
#        break
#
#  n = n+1
#


def neumeshapes(gabc_extended_table):
  table = gabc_extended_table
  shape = ""
  prev_neume = ""
  prev_gabc = ""
  prev_val = ""
  start_neume = 1
    
  for index in range(1,len(table)):
    curr_neume = table[index][colNeume]
    curr_gabc = table[index][colGABC]
    curr_val = table[index][colGABC][0].lower()
    ##table[index][colNeumeshape] = "undetermined"
    try:
      next_neume = table[index + 1][colNeume]
    except:
      next_neume = ""

    # Break condition
    if curr_neume in ("di", "cf"):
      neume_break = True
    elif table[index + 1][colSyllable] != "":
      neume_break = True
    elif re.search("/", curr_neume):
      neume_break = True
    else:
      neume_break = False
    if curr_neume == "vi":
      if next_neume not in ("vi", "pi"):
        neume_break = True
    if curr_neume == "pi":
      if next_neume != "pi":
        neume_break = True


    # Divisions
    if curr_neume == "di":
      shape = "division"
      table[index][colNeumeshape] = shape
      shape = ""
      continue

    if curr_neume == "cf":
      shape = "clef"
      table[index][colNeumeshape] = shape
      shape = ""
      continue

    # One note neumes
    if shape == "":
      #Punctum
      if curr_neume == "pu":
        shape = "punctum"
        start_neume = index
      
      #Virga
      if curr_neume == "vi":
        shape = "virga"
        start_neume = index


    # Two note neumes
    elif shape == "punctum":
      if curr_neume == "pu":
        if curr_val > prev_val:
          shape = "podatus"
        if curr_val == prev_val:
          shape = "distropha"
        if curr_val < prev_val:
          shape = "clivis"

    elif shape == "virga":
      if curr_neume == "vi":
        shape = "bivirga"
      if curr_neume == "pi":
        shape = "climacus-"
 
    
    # Three note neumes
    elif shape == "podatus":
      if curr_neume == "pu":
        if curr_val > prev_val:
          shape = "scandicus"
#        if curr_val == prev_val:
#          shape = ""
        if curr_val < prev_val:
          shape = "torculus"

    elif shape == "distropha":
      if curr_neume == "pu":
#        if curr_val > prev_val:
#          shape = ""
        if curr_val == prev_val:
          shape = "tristropha"
#        if curr_val < prev_val:
#          shape = ""

    elif shape == "clivis":
      if curr_neume == "pu":
        if curr_val > prev_val:
          shape = "porrectus"
#        if curr_val == prev_val:
#          shape = ""
#        if curr_val < prev_val:
#          shape = ""

    elif shape == "climacus-":
      if curr_neume == "pi":
        shape = "climacus"
    

    # Four note neumes
    elif shape == "climacus":
      if curr_neume == "pi":
        shape = "climacus+"
    
    elif shape == "climacus+":
      if curr_neume == "pi":
        shape = "climacus+"
    
    else:
      table[start_neume][colNeumeshape] = shape
      shape = ""
      continue
    # Five note neumes


    # print(index, start_neume, curr_gabc, curr_neume, shape, neume_break, curr_neume, next_neume)
    # Check if end of neume
      #print(index, neume_start, table[index][colSyllable], table[index][colNeume], curr_gabc, curr_neume, shape)
    if neume_break:
      table[start_neume][colNeumeshape] = shape
      shape = ""
      continue
    else:
      prev_neume = curr_neume
      prev_gabc = curr_gabc
      prev_val = curr_val
      continue


      # Bivirga
      # Punctum inclinatum
      # Podatus
      # Clivis
      # Epiphonus
      # Cephalicus
      # Scandicus
      # Salicus
      # Ancus
      # Torculus
      # Porrectus
      # Torculus resupinus
      # Porrectus flexus
      # Pes subpunctis
      # Scandicus subpunctis
      # Scandicus flexus
      # Climacus resupinus
      # Strophicus
      #  Pes strophicus
      # Clivis strophica
      # Torculus strophicus
      # Pressus
      # Quilisma
      # Compound neums


  return table

  #TODO test for if nextnote exists
#  for index in range(1,len(lycsv_table)):
#Test(currNote, prevNote)
#
#Checklist:
# - Break
# - Punctum
# -
#
#From GregorioNABC
# - StGall
#         * pu
#         * vi
# - Laon
#
#Unknown
#
#ALWAYS ADD Break condition (end of syllable, "/", Last I, ...)
#


def gabc2midi_table(gabc_extended_table):
  table = gabc_extended_table
  clef = "c3" #default value
  flat = ""
  neume = ""
  slur = ""
  linebreak = ""
  for index in range(1,len(table)):
    current_syllable = table[index][colSyllable]
    if len(current_syllable) > 0 and current_syllable[0] == " ":
      flat = ""
    current_gabc_note = table[index][colGABC]
    duration = 1
    #Turn off flat at word boundary
    if len(table[index][colSyllable]) > 0:
      if table[index][colSyllable][0] == " ":
        flat = ""
    if re.match(r"[a-mA-M]", current_gabc_note[0]):
      if "x" in current_gabc_note:
        flat = current_gabc_note[0]
        duration = 0
      if "y" in current_gabc_note:
        flat = ""
        duration = 0
      if "." in current_gabc_note:
        duration = 1.5
      if re.match(r"[cf][1-4]", current_gabc_note):
        clef = current_gabc_note[0:2]
        duration = 0
    if re.match(r'[z,;:{]', current_gabc_note):
      duration = 0
    if duration != 0 and re.match(r"[A-Ma-m]", current_gabc_note):
      current_midi_note = gabcnote2midi(current_gabc_note, clef, key_transpose, flat)
      #current_lily_note = midi2ly(current_midi_note, sharps)
    else:
      current_midi_note = ''
      #current_lily_note = ''
    table[index][colMIDI_value] = current_midi_note
    table[index][colDuration] = duration

  return table

###########
#From MIDI#
###########

def midi2ly(midivalue, sharps):
  #Adjust MIDI value
  midinote = int(midivalue)
  sharps = int(sharps)
#  if value % 12 == flat:
#    value -= 1
  octave = int(midinote / 12) - 1
  note = int(midinote % 12)
  if sharps > 0:
    lilynote = ('c', 'cis', 'd', 'dis', 'e', 'f', 'fis', 'g', 'gis', 'a', 'ais', 'b')[note]
  else:
    lilynote = ('c', 'des', 'd', 'ees', 'e', 'f', 'ges', 'g', 'aes', 'a', 'bes', 'b')[note]
  lilynote += (",, ", ", ", "", "'", "''", "'''", "''''")[octave - 1]
  return lilynote

def midi2ly_table(gabc_extended_table):
  table = gabc_extended_table
  for index in range(1,len(table)):
    current_midi_note = table[index][colMIDI_value]
    current_gabc_note  = table[index][colGABC]
    if current_midi_note != "":
      current_lily_note = midi2ly(current_midi_note, sharps)
      table[index][colLilyNote] = current_lily_note
    elif re.match('[z`,;:]', current_gabc_note) is not None:
      table[index][colLilyNote] = bar(current_gabc_note)
    else:
      continue
  return table
  

##########
#From CSV#
##########
#def read_csv(csv_filename):


def lilynotelength(duration):
  if duration == "0":
    return ''
  if duration == "1":
    length = "4"
  elif duration == "2":
    length = "2"
  elif duration == "1.5":
    length = "4."
  elif duration == "3":
    length = "2."
  elif ".5" in duration:
    durn = float(duration)
    durn *= 2
    duration = str(durn)
    length = ("2*" + duration + "/4")
  else:
    length = ("2*" + duration + "/2")
  if ".0" in length:
    length = length.replace('.0','')
  return length

###############
#From Lilypond#
###############

# Lilypond melody
def lily_melody(csv_table, slurs):
  data = csv_table
  melody = ""
  slur_array = lily_slurs(csv_table, slurs)
  slur_open = False
  
  for row in range(1,len(data)):
    current_lily_note = data[row][colLilyNote]

    if re.search("divisio", current_lily_note):
      current_lily_note += "\n"
    elif re.search("finalis", current_lily_note):
      current_lily_note += "\n\n"
    else:
      current_lily_note += " "
    
    # Start slur
    if slur_array[row] == 2:
      slur_open = True
      melody += "( "

    # End slur
    if slur_array[row] < 2 and slur_open == True:
      melody += ") "
      slur_open = False
    
    melody += current_lily_note

  print(melody)
  
#TODO Check Lilypond snippets and notation.pdf for ancient notation (chapter 17)
# How to avoid random linebreaks?

  # Clean up
  #melody = re.sub(r"\s{2,}", " ", melody)

  return melody

def lily_lyrics(csv_table, slurs):
  data = csv_table
  slur_array = lily_slurs(csv_table, slurs)
  lyrics = ""
  for row in range(1,len(data)):
    current_lily_syl = data[row][colSyllable]

    # Skip rows with empty Lilynote
    if data[row][colLilyNote] == "":
      continue

    # If syllable in previous row was skipped with non-empty syllable:
    if data[row - 1][colLilyNote] == "" and data[row - 1][colSyllable] != "":
      current_lily_syl = data[row - 1][colSyllable]

    #print(data[row][colIndex], current_lily_syl, data[row][colLilyNote], slur_array[row])
    if current_lily_syl != "":
      # Add -- to syllable breaks
      if current_lily_syl[0] != " ":
        lyrics += "-- "

      # Add syllable with a space
      lyrics += current_lily_syl + " "

    # Break line if finalis or divisio maxima
    divisions = ["divisio", "finalis"]
    large_divisions = ["divisioMaxima", "finalis"]
    if any(x in data[row][colLilyNote] for x in large_divisions):
      lyrics += "\n"
#    if re.search("divisioMaxima", data[row][colLilyNote]):
#    if re.search("finalis", data[row][colLilyNote]):

#    print(any(x in data[row][colLilyNote] for x in divisions))
#    print(any(x in divisions for x in data[row][colLilyNote]))
#    print(any(sub in data[row][colLilyNote] for sub in divisions))
#    print(current_lily_syl, re.search("Maxima", data[row][colLilyNote]))

    # TODO Add "_" between slurs if syllable break occurs within syllable
    #if slur_array[row] == 1 and data[row][colSyllable] == "" and any(x in data[row][colLilyNote] for x in divisions) == False:
    if slur_array[row] < 2 and slur_array[row - 1] >= 2:
      if data[row][colSyllable] == "":
        lyrics += "_ "

  # TODO Implement corrections from NOH script, eg *, scriptsize
  #  Also for \prall etc in lilymelody

  lyrics = lyrics.replace("**", "\n\\set stanza = \" ** \" ")
  lyrics = lyrics.replace("* ", "\n\\set stanza = \" * \" ")
  lyrics = lyrics.replace("scriptsize{", "markup { \\tiny ")
  lyrics = lyrics.replace("<v>", "")
  lyrics = lyrics.replace("</v>", "")


  return lyrics

#TODO
#Sequence: fill slurs, then melody
def lily_slurs(csv_table, option):
  # Options are:
  # "m": Manual
  # "w": Whole syllable
  # "s": Simple parse
  # "c": Complex parsing (attempts to emulate Gregorio)
  # "g": St. Gall neumes
  # "l": Laon neumes

  table = csv_table
  slur_array = [0] * len(csv_table)
  if option == "s":
    SimpleSlur = [None] * len(csv_table)
#   TODO see lily_simple_slur

  # Fill in slur array with 1 for first note in slur (or non-slurred)
# TODO Remember index of previous non-empty LilyNote to correct the slur numbering
#Try carry value over -- if skip == 1, stored = previous value. If condition met, slur = stored + 1; skip = 0, 
#Alternatively, skip if conditions are met for converting GABC to LILY (eg not a clef, not a flat, not a division...)
  slur_index = 0
  for index in range(1,len(slur_array)):
    ## Set to 0 if new syllable, division marker, new slur, etc.
    # Option specific
    if table[index][colSyllable] != "":
      slur_index = 0
    if option == "m":
      if table[index][colSlur] != "":
        slur_index = 0
    # TODO see lily_simple_slur
    if option == "s":
      if table[index][SimpleSlur] != "":
        slur_index = 0
    if option == "c":
      if table[index][colNeumeshape] != "":
        slur_index = 0
    if option == "g":
      if table[index][colSt_Gall] != "":
        slur_index = 0
    if option == "l":
      if table[index][colLaon] != "":
        slur_index = 0
    
    # All options
    if re.search("divisio", table[index][colLilyNote]):
      slur_index = 0
    if re.search("finalis", table[index][colLilyNote]):
      slur_index = 0
  
    # [Then] add one if colLilyNote contains a note
    if table[index][colLilyNote] != "":
      if table[index][colLilyNote][0] in "abcdefg":
        slur_index += 1
        slur_array[index] = slur_index

    print(table[index][colIndex], "\t", table[index][colSyllable], "\t", table[index][colGABC], "\t", table[index][colLilyNote], "\t", slur_index)


  # Fill in rest of array
#TODO prev_index, index
# for index in range(1,len(slur_array)):
#   if slur_array[index] == 0:
#     if table[index][colLilyNote] == "":
#      continue
#     else:
#       slur_array[index] = slur_array[prev_index] + 1

  return slur_array





##########
#From ABC#
##########

##############
#From Humdrum#
##############

##############
#From Verovio#
##############

####################
#From Caecilia Font#
####################

#########
#To GABC#
#########

def table2gabc(csv_table, gabc, sg, l):
  data = csv_table
  gabccode = ""

  # NABC options:
  # gabc: Include GABC
  # sg: Include St. Gall
  # l: Include Laon
  # TODO Add GABC metadata from colMetadata

  for i in range(1,len(data)):
    name_empty = True
    if data[i][colMetaValues] != "":
      metavalue = data[i][colMetaValues]
      metadata = data[i][colMetaValues]
      gabccode += metavalue + ":" + metadata + ";\n"
      if metavalue == "name":
        name_empty = False

  gabccode += "%%\n"
  if name_empty == True:
    gabccode = "name:;\n" + gabccode

  for i in range(1,len(data)):
    syllable = data[i][colSyllable]
    translation = data[i][colTranslation]
    gabc_note = data[i][colGABC]
    stgall_neume = data[i][colSt_Gall]
    laon_neume = data[i][colLaon]

    if translation != "":
      translation = "[" + translation + "]"

    if gabc_note != "":
      gabc_note = "(" + gabc_note + ")"

    if stgall_neume != "":
      stgall_neume = "|" + stgall_neume + "|"

    if laon_neume != "":
      laon_neume = "|" + laon_neume + "|"

    gabccode += syllable + translation + gabc_note + stgall_neume + laon_neume

  gabccode = re.sub("\)\(", "", gabccode)

  return gabccode

########
#To CSV#
########

#TODO def write_csv


#############
#To Lilypond#
#############

# Bars and divisions
def bar(sym):
  if "::" in sym:
    return "\\finalis"
#    return "\\doubleBar"
  if ":" in sym:
    return "\\divisioMaxima"
#    return "\\singleBar"
  if ";" in sym:
    return "\\divisioMaior"
#    return "\\halfBar"
  if "," in sym:
    return "\\divisioMinima"
#    return "\\quarterBar"
  if "`" in sym:
    return ""

############
#To Humdrum#
############

############
#To Verovio#
############

########
#To ABC#
########

##################
#To Caecilia Font#
##################

#
#TODO Read Lilupond input, CSV input, Humdrum input
#Functions read_LY, read_csv, _read_humdrum


#Read array: 
#for each column
#  determine if voice or notes from code (eg S1L is Soprano lyrics, B2N is 2nd Bass notes)
#  read column and durations in parallel

print(key_transpose)

#############
#START HERE:#
#############



#Options specific to input and output formats
#TODO Make this generic: re.sub(input$, output$, filename)
if args.from_gabc is True:
  gabc_filename = args.input_file
  if args.to_csv is True:
    csv_filename = re.sub(r'.gabc$', '.csv', gabc_filename)
  if args.to_lilypond is True:
    ly_filename = re.sub(r'.gabc$', '.ly', gabc_filename)
#  if args.to_abc is True:
#    abc_filename = re.sub(r'.gabc$', '.abc', gabc_filename)
#  if args.to_volpiano is True:
#    volpiano_filename = re.sub(r'.gabc$', '.', gabc_filename)
#  if args.to_humdrum is True:
#    humdrum_filename = re.sub(r'.gabc$', '.krn', gabc_filename)
#TODO Consider Meinrad and MIDI formats
    
#TODO if args.from_lilypond is True:
#TODO if args.from_csv is True:
#TODO if args.from_humdrum is True:
#TODO if args.from_abchumdrum is True:
#TODO if args.from_verovio is True:




