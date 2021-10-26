#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created on 14-06-2020 12:54:50

    Add new file types to fileutils to be saved/loaded by subclassing the fileio class. The new format will 
    be registered automatically and can be saved/loaded using fileutils.save/fileutils.load.
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"

from abc import abstractmethod, ABC

from importlib import import_module

from pprint import pprint
import traceback

class fdict(dict):
    """ 
        A dictionary for which key/value pairs cannot be overwritten once set.
    """

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __setitem__(self, k, v):
        if k not in self:
            super(fdict, self).__setitem__(k,v)
        else:
            raise KeyError("Key: {0} already exists.".format(k))

    def update(self, *args, **kwargs):
        for k,v in dict(*args, **kwargs).items():
            self[k] = v

class fileio(ABC):
    """ File IO class defines save and load methods for use in fileutils. Each fileio subclass should be unique (enforced) 
        to the particular file type as defined by the file extension. Subclassing this class will automatically register 
        the file type with fileutils enabling saveing and loading as defined the save/load methods of the subclass. A 
        dictionary of all avaliable file formats can be found: fileio.io 
    """

    io = fdict()
    __instances__ = {}

    def __new__(cls, *args, **kwargs):
        #print("NEW", cls)
        instance  = fileio.__instances__.get(cls, None)
        if instance is None:
            instance = super().__new__(cls, *args, **kwargs)
            fileio.__instances__[cls] = instance
        return instance

    def __init__(self, ext, *modules):
        #print("INIT", ext, modules)
        """ Create a new fileio object (which is a singleton).

        Args:
            ext (str): associated file extension.
            modules ([str]): any modules that should be loaded, modules can be accessed as using self.<module> where <module> is the base module 
            (i.e. if import foo.bar then self.foo) and are loaded using importlib.import_module. TODO fix problems with relative imports...
        """
        if ext not in fileio.io: #dont reload the class
            self.ext = ext
            fileio.io[self.ext] = self 
            
            for module in modules:
                if not isinstance(module, (tuple, list)):
                    module = (module,)
                try:
                    self.__dict__[module[0].split('.')[-1]] = import_module(*module)
                except:
                    print("WARNING: failed to find module: {0}".format(module[0]))
                    return #TODO warning or something?
        else:
            self.__dict__ = fileio.io[ext].__dict__ # TODO this needs a rethink

    @abstractmethod
    def save(self, *args, **kwargs):
        pass

    @abstractmethod
    def load(self, *args, **kwargs):
        pass


def supported_extensions():
    return list(fileio.io.keys())