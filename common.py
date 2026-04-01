#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys, os, re, argparse, getopt, io, csv

# TODO
# IMPLEMENTED TO LINE:  59
# TODO CURRENT
# Implement read
# TODO
# Write metadata function
# Search for value, if found then write to it
# if not found, add it then write
#
#TODO For direct conversions eg GABC to Lily
# Create CSV internally but do not write to file
#Or write file for corrections to be made
#
#TODO
#Logic for converting neumes to neumeshapes
#Logic for converting Meinrad to neumeshapes
#TODO
#Add option to specify number of NABC lines and specify StG/Laon
#Add option for NABC only (eg for transcribing E121)
#Add logic to detect StG or Laon if unspecified (or error message)
# TODO Add metadata from GABC
# TODO Finish transpose options
# TODO Add mode calculation to metadata
# TODO Replace "sharps" with "key signature"
# TODO How to add linebreaks?

# TODO
# Current columns: Syllable, GABC, Neume, Duration, MIDI value, LilyNote, Slur, Linebreak
# Add columns: Neume shape (podatus etc), Meinrad encoding, Caecilia encoding, ABC encoding, Humdrum encoding
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
parser.add_argument("-s", "--number_sharps", help="Number of sharps (negative for flats)")
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
parser.add_argument("-tc", "--to_csv", action="store_true", help="Output file is ")
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
headers = ['Index', 'Syllable', 'Translation', 'GABC', 'St. Gall', 'Laon', 'Neume', 'Neume shape', 'Duration', 'MIDI value', 'LilyNote', 'Slur', 'Linebreak', 'Meinrad', 'Caecilia', 'ABC', 'Humdrum', 'Metadata headers', 'Metadata values']

#TODO
#Add metadata values for name, key, annotation1, annotation2, key_signature, transpose, office-part, (book.page) reference,
#TODO add all GABC values to metadata columns
#Accepts all GABC headers

#Index values:
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
colMetaHeaders = 17
colMetaValues = 18
numCols = 19

#Notes
gabcnotes = ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m","n", "o", "p", "q", "r", "s", "t")
gabcnotes_caps = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M")
clef_adjust = {"c4":0, "c3":2, "c2":4, "c1":6, "f4":3, "f3":5, "f2":0, "f1":2}
gabcvalues = {"a":45, "b":47, "c":48, "d":50, "e":52, "f":53, "g":55, "h":57, "i":59, "j":60, "k":62, "l":64, "m":65, "n":67, "o":69, "p":71, "q":72, "r":74, "s":76, "t":77}

clef = "c3" #Default for Gregorio
flat = ''
ly_title = ''
ly_mode = ''
ly_genre = ''

#Key signature variables
lastnote = ''
lastmidi = 60
mode = {0:"major", 2:"dorian", 4:"phrygian", 5:"lydian", 7:"mixolydian", 9:"minor", 11:"locrian"}

#Transpose

#TODO Types of transpose
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

#4. Semitone adjust
if args.transpose_semitones is None:
  semitone_adjust = 0
else:
  semitone_adjust = int(args.transpose_semitones)
key_transpose += semitone_adjust

#1. Number of sharps
if args.number_sharps is not None:
  sharps = args.number_sharps
  if int(sharps) > 0:
    key_transpose = 7*int(sharps) % 12 + semitone_adjust
  else:
    key_transpose = 7*int(sharps) % 12 + semitone_adjust - 12
else:
  sharps = 0

#2 Transpose notes
if args.transpose_notes is not None:
  transpose_to_note = args.transpose_notes[1]
  transpose_from_note = args.transpose_notes[0]
  semitone_difference = transpose_values[transpose_to_note] - transpose_values[transpose_from_note]
  key_transpose += semitone_difference

#3 TODO
#Function read table[lynote], find semitone difference, adjust



#5 TODO
#Function read table[lynote], find semitone difference, adjust

#6 TODO
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
  #TODO Output these to colMetaHeaders and colMetaValues for other files to read
  gabc_data = {
    "gabcfile": "",
    "metadata": 1,
    "scorename": "",
    "officepart": "",
    "commentary": "",
    "mode": "",
    "annotation1": "",
    "annotation2": "",
    "nabclines": 0,
    "gabc_code": ""
    }

  #Read GABC input
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
      if re.match("^nabc-lines", line):
        nabclines = line
        nabclines = re.sub('^[^:]*:','', nabclines)
        nabclines = re.sub(';[^;]*$','', nabclines)
        gabc_data["nabclines"] = nabclines
  #     = line
  #     = re.sub('^[^:]*:','', )
  #     = re.sub(';[^;]*$','', )
      if re.match("^%%", line):
        gabc_data["metadata"] = 0
    else:
      gabc_code = gabc_code + line
  gabc_data["gabc_code"] = gabc_code
  return gabc_data

#TODO Add a translations column
#WARNING This might mess up order (Syl, Translation, GABC, SG, L)
#Convert gabc code to array of lyrics, individual notes, durations
def gabc2table(gabc: str) -> list:
  #Separate out Lyrics, GABC, NABC
  gabc_data = ""
  gabc_table = []
  gabc_table_long = []
  gabc_table_extended = []

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
  #Extend table
  for row in gabc_table_long:
    #Add NABC column if absent
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
    #Remove empty elements
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
  #Return table with [Syllable, Translation, GABC, NABC (St. Gall), NABC (Laon)]
  
  #Create full table
  gabc_full_table = []
  gabc_full_table.append(headers)
  for row in gabc_table_extended:
    row += [''] * (numCols - len(row))
    gabc_full_table.append(row)
  #Add index
  for index in range(1,len(gabc_full_table)):
    gabc_full_table[index][0] = index
  return gabc_full_table
#TODO print starting and ending notes

#TODO Turn flat on (flat = True) if x in GABC, keep flat on until end of word. (Detect new word if syllable[0] = " ")
def gabcnote2midi(gabcnote, clef, key_transpose, flat) -> int:
  gabcnotes = ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t")
  clef_adjust = {"c4":0, "c3":2, "c2":4, "c1":6, "f4":3, "f3":5, "f2":0, "f1":2}
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
      neume = "pu" #punctum
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

#Add slurs
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
  joinable_neumes = ("pu", "or", "qu", "li", "al", "dm", "ld", "vi", "pi")
  ignore = ("fl", "sh", "na")
  division = ("di", "cf")

  #for index in range(1,len(table)):
  index = 1
  while index < len(table):
    shape = ""
    neume1 = table[index][colNeume]
    gabc1 = table[index][colGABC]
    val1 = table[index][colGABC][0].lower()
    print(index)
    
    try:
      #Test if next index exists
      neume2 = table[index + 1][colNeume]
      gabc2 = table[index + 1][colGABC]
      val2 = table[index + 1][colGABC][0].lower()
      #Check if next neume exists and whether to continue
      if re.search("/", gabc1):
        break12 = True
      elif neume2 not in joinable_neumes:
        break12 = True
      elif table[index + 1][colSyllable] != "":
        break12 = True
      else:
        break12 = False
    except IndexError:
      neume2 = ""
      val2 = ""
      break12 = True
    
    try:
      neume3 = table[index + 2][colNeume]
      gabc3 = table[index + 2][colGABC]
      val3 = table[index + 2][colGABC][0].lower()
      if re.search(r"/", gabc2):
        break23 = True
      elif neume3 not in joinable_neumes:
        break23 = True
      elif table[index + 1][colSyllable] != "":
        break23 = True
      else:
        break23 = False
    except IndexError:
      neume3 = ""
      val3 = ""
      break23 = True
    
    try:
      neume4 = table[index + 3][colNeume]
      gabc4 = table[index + 3][colGABC]
      val4 = table[index + 3][colGABC][0].lower()
      if re.search(r"/", gabc3):
        break34 = True
      elif neume4 not in joinable_neumes:
        break34 = True
      elif table[index + 1][colSyllable] != "":
        break34 = True
      else:
        break34 = False
    except IndexError:
      neume4 = ""
      val4 = ""
      break34 = True
    
    try:
      neume5 = table[index + 4][colNeume]
      gabc5 = table[index + 4][colGABC]
      val5 = table[index + 4][colGABC][0].lower()
      if re.search(r"/", gabc4):
        break45 = True
      elif neume5 not in joinable_neumes:
        break45 = True
      elif table[index + 1][colSyllable] != "":
        break45 = True
      else:
        break45 = False
    except IndexError:
      neume5 = ""
      val5 = ""
      break45 = True
    
    #Break conditions:
    #End of word, end of syllable, "/" 
    
    #Shape codes: (check if implemented)
    #Punctum X
    #Virga X
    #Bivirga X
    #Punctum inclinatum
    #Podatus X
    #Clivis X
    #Epiphonus
    #Cephalicus
    #Scandicus
    #Salicus
    #Climacus
    #Ancus
    #Torculus
    #Porrectus
    #Torculus resupinus
    #Porrectus flexus
    #Pes subpunctis
    #Scandicus subpunctis
    #Scandicus flexus
    #Climacus resupinus
    #Strophicus
    #Pes strophicus
    #Clivis strophica
    #Torculus strophicus
    #Pressus
    #Quilisma
    #Compound neums
    
    #Zero note
    if neume1 not in joinable_neumes:
      index += 1
      continue
    #One note neumes
    if neume1 == "pu":
      shape = "punctum"
      if break12 is True:
        table[index][colNeumeshape] = shape
        index += 1
        continue
        
    if neume1 == "vi":
      shape = "virga"
      if break12 is True:
        table[index][colNeumeshape] = shape
        index += 1
        continue

    #Two note neumes
    if shape == "punctum":
      if neume2 == "pu":
        if val2 > val1:
          shape = "podatus"
          if break23 is True:
            table[index][colNeumeshape] = shape
            index += 2
            continue
        elif val2 == val1:
          shape = "strophicus2"
          if break23 is True:
            table[index][colNeumeshape] = shape
            index += 2
            continue
        else:
          shape = "clivis"
          if break23 is True:
            table[index][colNeumeshape] = shape
            index += 2
            continue

    if shape == "virga":
      if neume2 == "vi":
        if val2 == val1:
          shape = "bivirga"
          if break23 is True:
            table[index][colNeumeshape] = shape
            index += 2
            continue
      if neume2 == "pi":
        if neume3 == "pi":
          shape = "climacus"
          table[index][colNeumeshape] = shape
          index += 3
          continue

    #Three note neumes
    if shape == "podatus":
      if neume3 == "virga":
        if val3 > val2:
          shape = "scandicus"
          if break34 is True:
            table[index][colNeumeshape] = shape
            index += 3
            continue
      if neume3 == "pu":
        if val3 > val2:
          shape = "scandicus"
          if break34 is True:
            table[index][colNeumeshape] = shape
            index += 3
            continue
        if val3 == val2:
          shape = "pes strophicus"
          if break34 is True:
            table[index][colNeumeshape] = shape
            index += 3
            continue
        if val3 < val2:
          shape = "torculus"
          if break34 is True:
            table[index][colNeumeshape] = shape
            index += 3
            continue

    if shape == "strophicus2":
      if neume3 == "pu":
        if val3 == val2:
          shape = "strophicus3"
          if break34 is True:
            table[index][colNeumeshape] = shape
            index += 3
            continue

    if shape == "clivis":
      if neume3 == "pu":
        if val3 > val2:
          shape = "porrectus"
          if break34 is True:
            table[index][colNeumeshape] = shape
            index += 3
            continue
        if val3 == val2:
          shape = "clivis strophica"
          if break34 is True:
            table[index][colNeumeshape] = shape
            index += 3
            continue
        

    

    #Four note neumes
    

    #Five note neumes


    print("")
    #print(neume1,neume2,neume3,neume4,neume5)
    #print(val1,val2,val3,val4,val5)
    #print(gabc1,neume1,break12,break23,break34,break45)
    print(index, table[index][colSyllable], table[index+1][colSyllable], ":", shape, gabc1, neume1, break12)
    index += 1
    if shape == "":
      table[index][colNeumeshape] = str(index)
    table[index][colNeumeshape] = str(index)

# V Virga
# S stropha
# O oriscus
# I inclinatum
# M
# E punctum

# H Higher
# L Lower
# = Equal
# B Break
# I(+) Inclinatum
#punctum
#  H podatus
#     H scandicus
#     L torculus
#     I pes subpunctis
#     B podatus
#  I+ climacus
#  L clivis
#     H porrectus
#  L
#  0 bipunctum
#     H salicus
#  B punctum
#
#virga
#  V       bivirga
#    V       trivirga
#      I+      trivirga climacus
#    I+      bivirga climacus
#  I+ climacus


    #if neume1 == "pu":
    #  if 
    #if neume1 and neume2 in joinable:
#check value
#if not joinable then break
#if 
#Else table[index][colNeumeshape] = "porrectus"
#Check Gregorio documentation, NABC documentation, Liber for all names
#eg scandicus flexus 

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
    if re.match(r'[z,;:]', current_gabc_note):
      duration = 0
    if duration != 0:
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
    if current_midi_note != "":
      current_lily_note = midi2ly(current_midi_note, sharps)
      table[index][colLilyNote] = current_lily_note
    else:
      continue
  return table
  

##########
#From CSV#
##########
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

########
#To CSV#
########

#TODO def write_csv


#############
#To Lilypond#
#############

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




