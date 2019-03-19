#   Author:         Brandon Edelman
#   Major:          Information Technology
#   Creation Date:  February 17th 2019
#   Due Date:       February 22nd 2019
#   Course:         CSC223 020
  # Professor Name: Dr. Schwesinger
  # Assignment:     Assignment 3
  # Filename:       assignment3.py
  # Purpose:        To create a program that compares Moby Dick to the
  #                 variable stop_words and outputs the ten most used words.

import string
from variables import moby_dick, stop_words

# imported a counter to determine the most frequently used words
# cited at: https://docs.python.org/release/3.6.0/library/collections.html?highlight=counter#collections.Counter
from collections import Counter

# looping through each word in moby_dick to remove punctuation
no_punctuation = ""
for char in moby_dick:
    if char not in string.punctuation:
        no_punctuation = no_punctuation + char

# removing capitalization
dickArray = no_punctuation.lower()
# splitting to put the string into a list
dickArray = dickArray.split()

# list comprehension to remove the stop words from the array
newArray = [y for y in dickArray if y not in stop_words]
# passing the list into the counter
Counter = Counter(newArray)
# determining the most frequently used words from the list
most_occured = Counter.most_common(10)

# loop to output each word on their own line with count
for s in most_occured:
    print(s)
