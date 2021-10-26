#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created on 03-07-2020 12:46:30

    [Description]
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"

try: 
    import os
    import json
    from kaggle.api.kaggle_api_extended import KaggleApi

    from ..registry import register, registry, user_override

    global api
    api = None

    def authenticate(username=None, key=None):
        if username is None or key is None:
            # read ~/.kaggle/kaggle.json
            path = os.path.expanduser("~")
            path = os.path.join(path, ".kaggle\kaggle.json")    
            try:
                with open(path, "r") as fp:
                    cred = json.load(fp)
                    os.environ["KAGGLE_USERNAME"] = cred['username']
                    os.environ["KAGGLE_KEY"] = cred['key']
            except:
                raise ValueError("Failed to initialise kaggle, failed to find api key.")

        global api
        if api is None:
            api = KaggleApi()
        api.authenticate()

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
except:
    print("Failed to initialise kaggle.") 
