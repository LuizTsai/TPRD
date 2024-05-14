#!/usr/bin/python -u

import pdftotext
import sys

if len(sys.argv) < 2:
        print("Uso:", sys.argv[0],"[-v] <arquivo a carregar>")
        sys.exit()

nome_arq = sys.argv[1]

print(nome_arq)

# Load your PDF
with open(nome_arq, "rb") as f:
    pdf = pdftotext.PDF(f, physical=True)

# How many pages?
print(len(pdf))

# Iterate over all the pages
for page in pdf:
    print(page)

# Read some individual pages
print(pdf[0])
print(pdf[1])

# Read all the text into one string
print("\n\n".join(pdf))

