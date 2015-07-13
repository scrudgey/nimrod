# -*- coding: utf-8 -*-
"""Main routines for parsing specially-formatted context-free grammars and databases for the purpose
of generating general, randomized text.
"""
import os
import re

def load(path):
  """Load the grammar definition at path into a new dictionary.
  """

