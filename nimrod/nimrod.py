# -*- coding: utf-8 -*-
"""Context-free grammars and databases for
generating general, randomized text.
"""
import re
import random
import os
import logging


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

    <p|A|B>:
      insert "A" with probability p, otherwise insert "B"
      0.0 <= p <= 1.0

    <p|string>:
      insert "string" with probability p
      0.0 <= p <= 1.0

    {symbol}:
      replace {symbol} by a random entry in the definition of {symbol}.

    $varable:
      replace this $variable reference with its value, if set earlier. If $variable
      is not set, this reference will be replaced by empty string.

    $variable="value":
      sets variable $variable to have value "value".

    string $$variable
      this "lazy variable assignment" will assign $variable the value of the string.
      $$variable must come at the end of a line.
    """
    symbol_hook = re.compile(r'(\{(.+?)\})')
    prob_hook = re.compile(r'(<([\.\d]+)\|(.+?)>)')
    either_hook = re.compile(r'(<([\.\d]+)\|(.+?)\|(.+?)>)')
    var_ref_hook = re.compile(r'\$(\w+)')
    var_assign_hook = re.compile(r'(\W|^)\$(\w+)="(.+)"')
    var_lazy_assign_hook = re.compile(r' \$\$(\w+)$')

    logging.basicConfig(filename='debug.log',
                        filemode='w', level=logging.DEBUG)

    def __init__(self):
        self.symbols = {}
        self.path = None
        self.mtime = None
        self.variables = {}
        self.loaded_files = set()

    def interpret(self, symbol, parse=True, depth=0):
        """Return a random element of {symbol}.

        OPTIONAL ARGUMENTS:

        parse: bool (default True)
          True: parses the random element of {symbol}
          False: return the literal random element of {symbol}
        """
        if symbol in self.symbols:
            if parse:
                return self.parse(random.choice(self.symbols[symbol]), depth=depth)
            else:
                return random.choice(self.symbols[symbol])
        else:
            return '{'+symbol+'}'

    def ref(self, var):
        """Return the stored value of $var."""
        if var in self.variables:
            return self.variables[var]
        else:
            return ''

    def reset(self):
        """Clear all stored variable values."""
        self.variables = {}

    def parse(self, string, depth=0, **kwargs):
        """Process a string according to nimrod syntax with the loaded dictionary
        of symbols.
        """
        # TODO: elaborate the docstring here.

        # make sure we have the most up-to-date definition file
        self.check_file()
        # cache initial state
        initial_string = string
        logging.info('depth {}: '.format(depth)+' '*depth+'{}'.format(string))

        # catch variable assignments $variable=value
        for match in self.var_assign_hook.finditer(string):
            try:
                self.variables[match.group(2)] = match.group(3)
                logging.info('{} = {}'.format(match.group(2), match.group(3)))
            except:
                logging.debug('{} = {}'.format(match.group(2), match.group(3)))
                raise ParseVariableError("Could not assign variable.")
            string = string.replace(match.group(0), '', 1)

        # catch lazy variable assignment "string $$var"
        for match in self.var_lazy_assign_hook.finditer(string):
            rest = string.replace(match.group(0), '', 1)
            self.variables[match.group(1)] = rest
            string = rest

        # interpret either-or syntax <p|A|B>:
        for match in self.either_hook.finditer(string):
            if random.random() < float(match.group(2)):
                string = string.replace(match.group(0), match.group(3), 1)
            else:
                string = string.replace(match.group(0), match.group(4), 1)

        # interpret probability syntax <p|string>:
        for match in self.prob_hook.finditer(string):
            if random.random() < float(match.group(2)):
                string = string.replace(match.group(0), match.group(3), 1)
            else:
                string = string.replace(match.group(0), '', 1)

        # interpret symbol replacement {symbol}
        for match in self.symbol_hook.finditer(string):
            string = string.replace(match.group(
                1), self.interpret(match.group(2)), 1)

        # interpret variable references $variable
        for match in self.var_ref_hook.finditer(string):
            string = string.replace(match.group(
                0), self.ref(match.group(1)), 1)

        # include optional variable replacement {keyword}
        if kwargs:
            string = string.format(**kwargs)

        logging.info('depth {}: '.format(depth)+' '*depth+'{}'.format(string))
        # recurse until we reach a stable orbit or depth limit is reached
        if initial_string != string and depth < 100:
            return self.parse(string, depth=depth + 1, **kwargs)
        else:
            return string

    def default(self):
        """Return the default string, which is optionally defined in a dictionary
        under #default.
        """
        self.check_file()
        print(self.interpret('default'))

    def check_file(self):
        """Check to see if the file has changed.
        If it has, reload the file.
        """
        statbuf = os.stat(self.path)
        if self.mtime != statbuf.st_mtime:
            self.load(self.path)

    def load(self, path, append=False):
        """Load the grammar definition at path.

        OPTIONAL ARGUMENTS:
        append: bool (default False)
          if False, clear all symbols first.
        """
        if len(path) < 4 or path[-4] != '.txt':
            path = path + '.txt'
        if not append:
            self.loaded_files = set()
            self.symbols = {}
        self.path = path
        imports = []
        defmatch = re.compile(r'#')
        impmatch = re.compile(r'#import ([\w\.]+)')

        # store the file modification time
        statbuf = os.stat(self.path)
        self.mtime = statbuf.st_mtime

        # parse the definition file
        current_key = ''
        with open(path, 'r') as f:
            self.loaded_files.add(path)
            for line in f:
                line = line.rstrip()
                if not line:
                    continue
                match = defmatch.search(line)
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
            # TODO: test if circular imports are avoided
            if imp not in self.loaded_files:
                self.loaded_files.add(imp)
                working_dir = os.path.dirname(path)
                new_path = os.path.join(working_dir, imp)
                self.load(new_path, append=True)
