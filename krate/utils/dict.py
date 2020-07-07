#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created on 07-07-2020 14:24:32

    Useful dictionaries.
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"

class udict(dict):

    def __setitem__(self, k, v):
        if k in self:
            raise ValueError("Key {0} already exists.")
        super(udict, self).__setitem__(k,v)

    def update(self,*args,**kwargs):
        raise NotImplementedError() #TODO

