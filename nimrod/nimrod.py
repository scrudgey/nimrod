# -*- coding: utf-8 -*-
"""Main routines for parsing specially-formatted context-free grammars and databases for the purpose
of generating general, randomized text.
"""
import re
import random
import hashlib
import os

class grammar(object):
  """Base class contains the definitions for a series of grammatical symbols.
  It can interpret a symbol, which is a random process, or parse a string,
  which replaces each symbol with an interpretation.
  """
  symbol_hook = re.compile(r'(\{(.+?)\})')
  prob_hook = re.compile(r'(<([\.\d]+)\|(.+?)>)')
  #(\{([\d.]+)\|(.+?\}?.*?)\})

  def __init__(self):
    self.symbols = {}
    self.path = None
    self.mtime = None

  def interpret(self, symbol, raw=False):
    """Return a random element from the dictionary for a given symbol.
    """
    if symbol in self.symbols:
      if not raw:
        return self.parse(random.choice(self.symbols[symbol]))
      else:
        return random.choice(self.symbols[symbol])
    else:
      return '{'+symbol+'}'

  def parse(self, string, depth=0, **kwargs):
    """This is the main routine where the magic happens.
    Replace every instance of {symbol} in the string with a randomized entry
    from that symbol's definition.
    """
    self.check_hash()

    initial_string = string

    # interpret probability syntax {p|string}:
    for match in self.prob_hook.finditer(string):
      # import ipdb; ipdb.set_trace()
      if random.random() < float(match.group(2)):
        string = string.replace(match.group(0), match.group(3), 1)
      else:
        string = string.replace(match.group(0), '', 1)

    # interpret symbol replacement {symbol}
    for match in self.symbol_hook.finditer(string):
      string = string.replace(match.group(1), self.interpret(match.group(2)), 1)

    # include optional variable replacement
    if kwargs:
      string = string.format(**kwargs)

    # iterate
    if initial_string != string and depth < 10:
      return self.parse(string, depth=depth + 1, **kwargs)
    else:
      return string

  def run(self):
    """Interpret the default string, which is defined in a dictionary
    as #default.
    """
    self.check_hash()
    print self.interpret('default')

  def check_hash(self):
    """Check to see if the file has changed since we last run.
    If it has, reload the file.
    """
    statbuf = os.stat(self.path)
    if self.mtime != statbuf.st_mtime:
      print "file updated. loading..."
      self.load(self.path)

  def load(self, path):
    """Load the grammar definition at path into a new dictionary.
    """
    self.symbols = {}
    self.path = path

    catmatch = re.compile(r'#')

    statbuf = os.stat(self.path)
    self.mtime = statbuf.st_mtime

    current_key = ''
    with open(path, 'r') as f:
      for line in f:
        line = line.rstrip()
        if not line: continue
        match = catmatch.search(line)
        if match:
          current_key = line[1:]
        if not match:
          items = self.symbols.get(current_key, [])
          items.append(line)
          self.symbols[current_key] = items

