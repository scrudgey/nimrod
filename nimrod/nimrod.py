# -*- coding: utf-8 -*-
"""Main routines for parsing specially-formatted context-free grammars and databases for the purpose
of generating general, randomized text.
# """
# import os
import re
import random

#1. interpret and get a string back
#2. check the string for any further parsing. if not, done
#3. if further parsing, increase depth counter and go to 1.

class grammar(object):

  symbol_hook = re.compile(r'(\{(.+?)\})')

  def __init__(self):
    self.symbols = {}

  def interpret(self, symbol):
    """Return a random element from the dictionary for a given symbol.
    """
    if symbol in self.symbols:
      return random.choice(self.symbols[symbol])
    else:
      return None

  def parse(self, string, depth=0):
    """This is the main routine where the magic happens.
    """
    initial_string = string
    for match in self.symbol_hook.finditer(string):
      # print "%s: %s" % (match.start(), match.group(2))
      string = string.replace(match.group(1), self.interpret(match.group(2)), 1)
    if initial_string != string and depth < 10:
      return self.parse(string, depth=depth + 1)
    else:
      return string

def load(path):
  """Load the grammar definition at path into a new dictionary.
  """
  catmatch = re.compile(r'#')
  gram = grammar()
  current_key = ''
  with open(path, 'r') as f:
    for line in f:
      line = line.rstrip()
      if not line: continue
      match = catmatch.search(line)
      if match:
        current_key = line[1:]
      if not match:
        items = gram.symbols.get(current_key, [])
        items.append(line)
        gram.symbols[current_key] = items

        # gram.symbols[current_key] = gram.symbols.get(current_key, []).append(line)
  print gram.parse('{noun} is {noun}')
  return gram

