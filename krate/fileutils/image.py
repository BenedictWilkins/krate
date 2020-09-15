#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created on 14-06-2020 14:01:28

    File IO for common image formats.
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"


from .fileio import fileio

#TODO refactor these at some point...?

class pngIO(fileio):

    def __init__(self):
        super(pngIO, self).__init__('.png', 'cv2')

    def save(self, file, data):
        self.cv2.imwrite(file, data)

    def load(self, file):
        return self.cv2.imread(file)

class tifIO(fileio):
    def __init__(self):
        super(tifIO, self).__init__('.tif', 'cv2')

    def save(self, file, data):
        self.cv2.imwrite(file, data)

    def load(self, file):
        return self.cv2.imread(file)

class jpegIO(fileio):
    def __init__(self):
        super(jpegIO, self).__init__('.jpeg', 'cv2')

    def save(self, file, data):
        self.cv2.imwrite(file, data)

    def load(self, file):
        return self.cv2.imread(file)
    
class jpegIO2(fileio):

    def __init__(self):
        super(jpegIO2, self).__init__('.jpg', 'cv2')

    def save(self, file, data):
        self.cv2.imwrite(file, data)

    def load(self, file):
        return self.cv2.imread(file)

class bmpIO(fileio):

    def __init__(self):
        super(bmpIO, self).__init__('.bmp', 'cv2')

    def save(self, file, data):
        self.cv2.imwrite(file, data)

    def load(self, file):
        return self.cv2.imread(file)



    
