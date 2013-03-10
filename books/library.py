#!/usr/bin/env python

import os
import sys

"""
Like a service locator for book resources.
As a module to be a singleton.
"""


_resources = {}

def list():
  """ Return list of Resources available in this library.
  """
  return _resources.keys()

def get(name):
  """ Retrieve resource of this name.
  """
  return _resources.get(name)

def add(name, resource):
  """ Add item to the library.
  """
  _resources[name] = resource