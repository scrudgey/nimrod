# -*- coding: utf-8 -*-
"""Main routines for parsing specially-formatted context-free grammars and databases for the purpose
of generating general, randomized text.
"""
import re
import random

class grammar(object):
  """Base class contains the definitions for a series of grammatical symbols.
  It can interpret a symbol, which is a random process, or parse a string,
  which replaces each symbol with an interpretation.
  """
  symbol_hook = re.compile(r'(\{(.+?)\})')

  def __init__(self):
    self.symbols = {}

  def interpret(self, symbol, raw=False):
    """Return a random element from the dictionary for a given symbol.
    """
    if symbol in self.symbols:
      if not raw:
        return self.parse(random.choice(self.symbols[symbol]))
      else:
        return random.choice(self.symbols[symbol])
    else:
      return None

  def parse(self, string, depth=0):
    """This is the main routine where the magic happens.
    Replace every instance of {symbol} in the string with a randomized entry
    from that symbol's definition.
    """
    initial_string = string
    for match in self.symbol_hook.finditer(string):
      string = string.replace(match.group(1), self.interpret(match.group(2)), 1)
    if initial_string != string and depth < 10:
      return self.parse(string, depth=depth + 1)
    else:
      return string

  def run(self):
    """Interpret the default string, which is defined in a dictionary
    as #default.
    """
    print self.interpret('default')

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
  return gram

