#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created on 24-11-2020 15:55:10

    [Description]
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"

import os
import re

from ..fileutils import load

class Node:

    def __init__(self, name):
        super(Node, self).__init__()
        self.name = name
        self.parent = None
        self.__children = {}

    def add_child(self, *child):
        for c in child:
            self.__children[os.path.splitext(c.name)[0]] = c
            c.parent = self

    def __getitem__(self, k):
        return self.__children[k]

    @property
    def children(self):
        return list(self.__children.values())

    @property
    def path(self):
        if self.parent is not None:
            return os.path.join(self.parent.path, self.name)
        return self.name

    @property
    def root(self):
        if self.parent is not None:
            return self.parent.root()
        else:
            return self

    def load(self, *args, **kwargs):
        pass 

    def __str__(self, inc=0):
        return (" " * inc) + self.name + "\n" + "".join([c.__str__(inc+2) for c in self.children])

    def __repr__(self, inc=0):
        return str(self)


class FNode(Node):

    def __init__(self, path):
        name = os.path.split(path)[1]
        super(FNode, self).__init__(name)
 
    def add_child(self, child):
        raise ValueError("Cannot add child to file node {0}".format(self.name))

    def load(self, *args, **kwargs):
        return load(self.path, *args, **kwargs)

    @property
    def ext(self):
        return os.path.splitext(self.name)

class DNode(Node):
    
    def __init__(self, path):
        name =  os.path.split(path)[1]
        super(DNode, self).__init__(name)

    @property
    def files(self):
        return self.children

    def load(self):
        raise NotImplementedError("TODO")
    
def traverse(path, bl=['$^']):
    """ Traverse the directory structure and retrive all 
        matching files/directories in the form a tree.

    Args:
        path (str): root directory
        bl (list): blacklist (files to exclude)
    """
    if bl is None:
        bl = ['$^']

    bl = re.compile('|'.join([w for w in bl]))

    def _traverse(path, root):
        path, dirs, files = next(os.walk(path))
        root.add_child(*[FNode(os.path.join(path, f)) for f in files if bl.match(f) is None])
        
        for d in dirs:
            dpath = os.path.join(path, d)
            dnode = DNode(dpath)
            root.add_child(dnode)
            _traverse(dpath, dnode)
        
    path = os.path.expanduser(path)
    path = os.path.abspath(path)

    path, dirs, files = next(os.walk(path))

    root = DNode(path)
    root.add_child(*[FNode(os.path.join(path, f)) for f in files if bl.match(f) is None])
    
    for d in dirs:
        dpath = os.path.join(path, d)
        dnode = DNode(dpath)
        root.add_child(dnode)
        _traverse(dpath, dnode)

    root.name = path # should be a full path of the dataset...
    return root



if __name__ == "__main__":
 
    root = traverse("~/Documents/repos/krate/krate/utils", ["^.*\.py$"]) 
    
    bl = re.compile('|'.join([w for w in ["^.*\.py$"]]))
    
    print(bl.match("test.pyc"))
    print(root)