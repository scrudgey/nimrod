# -*- coding: utf-8 -*-
"""Main routines for parsing specially-formatted context-free grammars and databases for the purpose
of generating general, randomized text.
"""
import re
import random
import os
import logging

#TODO: define comments in the definition file

class ParseVariableError(Exception):
  """Exception for errors in assigning or parsing nimrod variables."""
  def __init__(self, message):
    super(ParseVariableError, self).__init__(message)
    self.message = message

class Grammar(object):
  """The grammar object loads a grammar defined in an external file via the load()
  method. It can then parse() arbitrary strings for symbols defined in its loaded dictionary.
  ----------
  SYNTAX:

  {symbol}:
    nimrod will replace {symbol} by a random entry from its definition of {symbol}.

  <p|string>:
    nimrod will insert "string" with probability p

  $variable=value:
    this will define variable $variable to have value "value" for all following strings.

  string $$variable
    this "lazy variable assignment" will assign $variable the value of the string.
    Must come at the end of a line.

  $varable:
    nimrod will replace this $variable reference with its value, if set earlier. If $variable
    is not set, this reference will be replaced by empty string.

  """
  symbol_hook = re.compile(r'(\{(.+?)\})')
  prob_hook = re.compile(r'(<([\.\d]+)\|(.+?)>)')
  var_ref_hook = re.compile(r'\$(\w+)')
  var_assign_hook = re.compile(r'(\W|^)\$(\w+)=([\w\{\}-]+)')
  var_lazy_assign_hook = re.compile(r' \$\$(\w+)$')

  def __init__(self):
    self.symbols = {}
    self.path = None
    self.mtime = None
    self.variables = {}
    self.loaded_files = []

  def interpret(self, symbol, raw=False):
    """Return a random element from the dictionary for a given symbol."""
    if symbol in self.symbols:
      if not raw:
        return self.parse(random.choice(self.symbols[symbol]))
      else:
        return random.choice(self.symbols[symbol])
    else:
      return '{'+symbol+'}'

  def ref_var(self, var):
    """Similar to interpret, but replace the variable reference with its value in the variables
    dictionary. Else return blank string.
    """
    if var in self.variables:
      return self.variables[var]
    else:
      return ''

  def reset(self):
    """Clear all stored variable values."""
    self.variables = {}

  def parse(self, string, depth=0, **kwargs):
    """This is the main routine where the magic happens.
    Replace every instance of {symbol} in the string with a randomized entry
    from that symbol's definition.

    Pass arbitrary keywords to
    """
    self.check_hash()
    initial_string = string

    logging.info('starting parse at depth %s', depth)
    logging.info(string)

    # catch variable assignments $variable=value
    for match in self.var_assign_hook.finditer(string):
      try:
        self.variables[match.group(2)] = match.group(3)
      except:
        raise ParseVariableError("Could not assign variable.")
      string = string.replace(match.group(0), '', 1)

    # catch lazy variable assignment "string $$var"
    for match in self.var_lazy_assign_hook.finditer(string):
      rest = string.replace(match.group(0), '', 1)
      self.variables[match.group(1)] = rest
      string = rest

    # interpret probability syntax {p|string}:
    for match in self.prob_hook.finditer(string):
      if random.random() < float(match.group(2)):
        string = string.replace(match.group(0), match.group(3), 1)
      else:
        string = string.replace(match.group(0), '', 1)

    # interpret symbol replacement {symbol}
    for match in self.symbol_hook.finditer(string):
      string = string.replace(match.group(1), self.interpret(match.group(2)), 1)

    # interpret variable references $variable
    for match in self.var_ref_hook.finditer(string):
      string = string.replace(match.group(0), self.ref_var(match.group(1)), 1)

    # include optional variable replacement {keyword}
    if kwargs:
      string = string.format(**kwargs)

    # iterate
    if initial_string != string and depth < 10:
      return self.parse(string, depth=depth + 1, **kwargs)
    else:
      return string

  def run(self):
    """Interpret the default string, which is defined in a dictionary
    under #default.
    """
    self.check_hash()
    print self.interpret('default')

  def check_hash(self):
    """Check to see if the file has changed.
    If it has, reload the file.
    """
    statbuf = os.stat(self.path)
    if self.mtime != statbuf.st_mtime:
      self.load(self.path)

  def load(self, path, reset_loaded=True):
    """Load the grammar definition at path into a new dictionary."""
    if reset_loaded:
      self.loaded_files = []
    self.symbols = {}
    self.path = path
    imports = []
    catmatch = re.compile(r'#')
    impmatch = re.compile(r'#import ([\w\.]+)')

    # store the file modification time
    statbuf = os.stat(self.path)
    self.mtime = statbuf.st_mtime

    # parse the definition file
    current_key = ''
    with open(path, 'r') as f:
      self.loaded_files.append(path)
      for line in f:
        line = line.rstrip()
        if not line: continue
        match = catmatch.search(line)
        if match:
          import_match = impmatch.search(line)
          if import_match:
            imports.append(import_match.group(1))
          else:
            current_key = line[1:]
        if not match:
          items = self.symbols.get(current_key, [])
          items.append(line)
          self.symbols[current_key] = items

    for imp in imports:
      # watch the fuck out for circular imports!!!
      # i try to catch them here but who knows if this will work for all cases
      if imp not in self.loaded_files:
        self.loaded_files.append(imp)
        working_dir = os.path.dirname(path)
        new_path = os.path.join(working_dir, imp)
        self.load(new_path, reset_loaded=False)

