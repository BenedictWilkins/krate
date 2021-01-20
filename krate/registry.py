#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created on 03-07-2020 15:26:43

    When ever a new dataset is created (or downloaded) it should be registered.
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"

import os 
import json

KRATE_DEFAULT_PATH = os.path.normpath(os.path.expanduser("~/.krate/"))
KRATE_REGISTRY_PATH = os.path.join(KRATE_DEFAULT_PATH, ".registry.json")

def registry():
    if not os.path.exists(os.path.split(KRATE_REGISTRY_PATH)[0]):
        os.mkdir(os.path.split(KRATE_REGISTRY_PATH)[0])
        with open(KRATE_REGISTRY_PATH, 'w') as f:
            f.write("{}")

    with open(KRATE_REGISTRY_PATH, 'r') as f:
        registry = json.load(f)
    return registry

def validate_registry():
    reg = registry()
    #check that all of the data is still there
    for k in list(reg.keys()):
        if not os.path.isdir(reg[k]['path']):
            del reg[k]
    
    with open(KRATE_REGISTRY_PATH, 'w') as f:
        json.dump(reg, f)

validate_registry() #validate the registry (remove anything that has been deleted)

def register(name, path, force=True, **kwargs):
    path = os.path.expanduser(path)

    if not os.path.exists(path): # try looking in default location .krate
        dpath = os.path.normpath(os.path.join(KRATE_DEFAULT_PATH, path))
        if not os.path.exists(dpath):
            raise OSError("Failed to find dataset directory: {0}".format(path))
        path = dpath

    entry = dict(path=path, **kwargs)

    if not os.path.isfile(KRATE_REGISTRY_PATH): #what happend...
        with open(KRATE_REGISTRY_PATH, 'w+') as f:
            json.dump(dict())

    with open(KRATE_REGISTRY_PATH, 'r') as f:
        registry = json.load(f)
    
    registry[name] = entry

    with open(KRATE_REGISTRY_PATH, 'w') as f:
        json.dump(registry, f)
    return True

def rename(old_name, new_name):
    with open(KRATE_REGISTRY_PATH, 'r') as f:
        registry = json.load(f)
    
    if new_name in registry:
        raise ValueError("A dataset already exists with name: {0}".format(new_name))

    registry[new_name] = registry[old_name]
    del registry[old_name]

    with open(KRATE_REGISTRY_PATH, 'w') as f:
        json.dump(registry, f)


def remove(name):
    """ Completely remove a dataset (including all files).

    Args:
        name (str): dataset name.
    """
    reg = registry()
    if not name in reg:
        print("dataset: \"{0}\" not found in registry.".format(name))
        return 

    path = reg[name]['path']
    print("removing dataset: \"{0}\" from location:{1}".format(name, path))
    for root, dirs, files in os.walk(path, topdown=False):
        print(root, dirs, files)
        for f in files:
            f = os.path.join(root, f)
            print("removing file: {0}".format(f))
            os.remove(f)
        os.rmdir(root)
    
    #remove all datasets that used this data from the registry
    for k in list(reg.keys()):
        if path == reg[k]['path']:
            del reg[k]

    with open(KRATE_REGISTRY_PATH, 'w') as f:
        json.dump(reg, f)

def user_override():
    invalid = True
    while invalid:
        print("dataset: \"{0}\" already exists at location:\n{1}\noverwrite it? [y/n]".format(name, registry[name]['path']))
        i = input()
        if i == 'n':
            print("aborting.")
            return False
        elif i == 'y':
            return True
        print("please type [y/n].")




    
