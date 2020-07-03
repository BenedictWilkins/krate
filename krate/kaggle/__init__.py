#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created on 03-07-2020 12:46:30

    [Description]
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"

import os
from kaggle.api.kaggle_api_extended import KaggleApi

from ..registry import register, registry, user_override

def authenticate(username, key):
    os.environ["KAGGLE_USERNAME"] = username
    os.environ["KAGGLE_KEY"] = key
    api.authenticate()

api = KaggleApi()
authenticate("benedictwilkinsai", "959b5f285c9be16588f97f87267be2a5")

def datasets(search=None, user=None):
    return api.dataset_list(search=search)

def download(name, path="~/.krate/", force=False, alias=None):
    if alias is None:
        alias = name

    if path.startswith("~"):
        path = os.path.expanduser(path)
    path = os.path.join(path, name)
    path = os.path.abspath(path)
    
    api.dataset_download_files(name, quiet=False, unzip=True, force=force, path=path)
    register(alias, path)

if __name__ == "__main__":
    print(datasets('mnist'))
    download('mnist-hd5f')
