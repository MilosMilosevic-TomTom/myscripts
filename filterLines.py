#!/usr/bin/python

import sys
import re

if len(sys.argv) < 4:
  print("Usage: ./filterLines <input_file> 'containing/not-containing' <search_phrase> <output_file>")

input_file_name = sys.argv[1]
contating = sys.argv[2] == "containing"
phrase = sys.argv[3]
output_file_name = sys.argv[4] if len(sys.argv) == 5 else "filtered.txt"

print("Extracting lines {} {} from {} and outputing to {}".format("containing" if contating else "not containing", phrase, input_file_name, output_file_name))

input_file = open(input_file_name, "r")
output_file = open(output_file_name, "w")

for line in input_file:
  if (contating) and re.search(phrase, line, re.IGNORECASE):
    output_file.write(line)
  elif (not contating) and (phrase not in line):
    output_file.write(line)