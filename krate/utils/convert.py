#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created on 04-08-2020 19:18:46

    [Description]
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"

import os
import numpy as np

from pprint import pprint

from .. import fileutils as fu


def images2video(path, image_extension, video_path=None, sortby=lambda x: x, verbose=False):
    """ Convert a collection of images to video.

    Args:
        path ([type]): [description]
        image_extension ([type]): [description]
        video_extension (str, optional): [description]. Defaults to '.hdf5'.
        sortby ([type], optional): [description]. Defaults to lambdax:x.
    """
    if video_path is None:
        video_path = os.path.join(path, "video.hdf5")

    files = fu.files_with_extention(path, image_extension, full=True)
    files = sorted(files, key=sortby)
    if verbose:
        print("Converting {0} images...".format(len(files)))
    data = [fu.load(f) for f in files]
    data = np.stack(data)
    if verbose:
        print("Done: {0}".format(data.shape))
    fu.save(video_path, data, force=True, overwrite=False)

