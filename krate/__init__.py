#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created on 03-07-2020 12:29:28

    [Description]
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"

import os

from . import kaggle
from . import registry

__all__ = ('kaggle', 'registry')



class Dataset:

    def __init__(self, name, **kwargs):
        self.name = name
        self.path = kwargs['path']
        self.meta = kwargs    

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)
    
def datasets(path="~/.krate/"):
    return __datasets__

__datasets__ = {name:Dataset(name, **kwargs) for name, kwargs in registry.registry().items()}




