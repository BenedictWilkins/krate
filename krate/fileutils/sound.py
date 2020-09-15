#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created on 14-06-2020 14:01:54

    File IO for common sound formats.
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"

from .fileio import fileio

# TODO finish this
class WavIO(fileio):

    def __init__(self):
        super(WavIO, self).__init__('.wav', 'scipy.io.wavfile')
    
    def save(self, file, data):
        raise NotImplementedError()

    def load(self, file):
        return self.wavfile.read(file)
