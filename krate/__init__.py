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


__all__ = ('kaggle', 'registry')

FILE_GROUP_PATTERN = "([a-zA-Z0-9\s_\\.\-\(\):]*)\(([0-9]+)\)\.[a-zA-Z0-9\s_\\.\-\(\):]+$"

class LoadGenerator:

    def __init__(self, files):
        self.__files = files
        self.__iter = iter(files)

    def __len__(self):
        return len(self.__files)

    def __iter__(self):
        return self

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.__files[key].load()
        else:
            return [f.load() for f in self.__files[key]]

    def __next__(self):
        return next(self.__iter).load()

class filegroup(dict):
    """ 
        A group of files that may be loaded as one, groups are indicated by file name: file(i).ext
    """
    def __init__(self):
        super().__init__()
        self.order = []

    def load(self):
        #sort the group... TODO make more efficient...? (the dataset will probably only be loaded once, so this is ok?)
        sorted_files = sorted(list(self.keys()), key=lambda x:int(re.match(FILE_GROUP_PATTERN, x).group(2)))
        files = [self[f] for f in sorted_files]
        return LoadGenerator(files)

    def load_as(self):
        raise NotImplementedError("TODO") #TODO

class ddict(dict):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__dict__.update(**kwargs)

    def __setitem__(self, k, v):
        if k in self.__dict__:
            raise KeyError("Key {0} already exists.")
        super().__setitem__(k, v) #always add the file to the file dict
        self.__dict__[k] = v
    
    def update(self, d):
        super().update(d)
        self.__dict__.update(d)

    def __delitem__(self, k):
        super().__delitem__(k)
        del self.__dict__[k]

class fdict(dict):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__filegroups = defaultdict(filegroup)
        self.__dict__.update(**kwargs)

    def __setitem__(self, k, v):
        if k in self:
            raise KeyError("Key {0} already exists.".format(k))
        super().__setitem__(k, v) #always add the file to the file dict

        #does the file belong to a group?
        match = re.match(FILE_GROUP_PATTERN, v.file)
        if match is not None: # if the file name matches, the file should be part of a group -- file(i).ext and may be loaded as such
            group = match.group(1)
            self.__filegroups[group][v.file] = v
            self.__dict__[group] = self.__filegroups[group]
        else:
            #create new file group (might be unique)
            if not v.name in self.__filegroups:
                self.__dict__[k] = v #if the node turns out not to be part of a group, this is fine.
            self.__filegroups[v.name][v.name + "(0)" + v.extension] = v #add it as the first element of a group, may be unused
    
    def update(self, d):
        super().update(d)
        self.__dict__.update(d)

    def __delitem__(self, k):
        super().__delitem__(k)
        del self.__dict__[k]

class DNode:

    def __init__(self, name):
        self.__parent = None
        self.__name = name
        self.dirs = ddict()
        self.files = fdict()

    def load(self):
        return SimpleNamespace(**self.dirs, **{v.name:v for v in self.files.values()})

    @property
    def path(self):
        return os.path.join(self.parent.path, self.name)
    
    @property 
    def parent(self):
        return self.__parent

    @property
    def name(self):
        return self.__name

    def __str__(self, space=0):
        return ("    " * space) + self.name + "".join("\n" + v.__str__(space+1) for v in self.files.values()) + "".join("\n" + v.__str__(space+1) for v in self.dirs.values())

    def __repr__(self):
        return self.name

    def to_dict(self):
        return {k:v.to_dict() for k,v in self.dirs.items()}

    def __getitem__(self, k):
        if k in self.dirs:
            return self.dirs[k]
        elif k in self.files:
            return self.files[k]
        else:
            raise KeyError("Invalid key: {0}".format(k))

class FNode:

    def __init__(self, parent, file):
        self.__parent = parent
        self.__name, self.__ext = os.path.splitext(file)

    def load(self):
        return fileutils.load(self.path)

    @property 
    def parent(self):
        return self.__parent

    @property
    def name(self):
        return self.__name
    
    @property
    def extension(self):
        return self.__ext

    @property
    def file(self):
        return self.name + self.extension

    @property
    def path(self):
        return os.path.join(self.parent.path, self.file)

    def __str__(self, space=0):
        return ("    " * space) + self.file

    def __repr__(self):
        return str(self)

class RootNode(DNode):
    
    @property
    def path(self):
        return self.__path

class Dataset(RootNode):

    def __init__(self, name, **kwargs):
        super(Dataset, self).__init__(name)
        self.__path = kwargs['path']
        self.meta = kwargs 

        nodes = {}
        for root, dirs, files in os.walk(self.path, topdown=False):
            node = DNode(os.path.split(root)[1])
            nodes[root] = node

            for child in dirs:
                node.dirs[child] = nodes[os.path.join(root, child)]
                node.dirs[child]._DNode__parent = node
            
            for file in files:    
                fnode = FNode(node, file)
                node.files[fnode.name] = fnode

        self.dirs = node.dirs
        for n in self.dirs.values():
            n._DNode__parent = self
        self.files = node.files
        for f in self.files.values():
            f._FNode__parent = self


    @property
    def path(self):
        return self.__path
    
def datasets(path="~/.krate/"):
    #TODO check for registry updates? only create the dataset if it is requested
    return {name:Dataset(name, **kwargs) for name, kwargs in registry.registry().items()}

def load(name):
    try:
        ds = datasets()[name]
        return ds.load()
    except:
        raise KeyError("Failed to find dataset, see krate.datasets() for a list of locally avaliable datasets.")


def new(dataset, name, path=None):
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

__datasets__ = {name:Dataset(name, **kwargs) for name, kwargs in registry.registry().items()}




