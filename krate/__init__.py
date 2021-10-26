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
import re
from tqdm.auto import tqdm
from types import SimpleNamespace
from collections import defaultdict

import bisect

from . import kaggle
from . import registry
from . import fileutils
from . import utils
from . import transform

# convenience imports
from .fileutils import supported_extensions

from .registry import register

__all__ = ('kaggle', 'registry')


FILE_GROUP_PATTERN = "([a-zA-Z0-9\s_\\.\-\(\):]*)\(([0-9]+)\)\.[a-zA-Z0-9\s_\\.\-\(\):]+$"


def datasets(path="~/.krate/"):
    #TODO check for registry updates? only create the dataset if it is requested
    return {k:v for k,v in registry.registry().items()}

def dataset(name):
    meta = registry.registry()[name]
    try:
        path = meta['path']
        bl = meta.get('blacklist', None)
        return utils.tree.traverse(path, bl)
    except Exception as e:
        raise ValueError("Invalid dataset meta, check ~/.krate/.registry for issues", e)




# TOOD refactor?
def new(dataset, name, path="~/.krate/"):
    """ Create a new dataset and save it to disk.

    Args:
        dataset (dict): dictionary of data, (k,v) k=file/directory path (relative), v=data/dictionary of data
        name (str): name of the dataset
        path (str, optional): path of the dataset. Defaults to "~/.krate/<name>".
    """
   
    def new_dir(root, dataset, indent=0):
        assert isinstance(dataset, dict)
        for k,v in dataset.items():
            split = os.path.splitext(k)
            if split[1] != '':
                print("--"*indent, k)
                name, ext = split
                fileutils.save(os.path.join(root,k),v)
            else:
                print("--"*indent, k)
                path = os.path.join(root, k)
                os.makedirs(path)
                new_dir(path, v, indent+1)
                
    if path is None:
        path =  os.path.expanduser("~/.krate/")
        path = os.join(path, name)
    
    new_dir(path, dataset)




