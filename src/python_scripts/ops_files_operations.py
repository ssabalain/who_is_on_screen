import ops_check_packages as cp

packages_required = ["pandas","requests"]

for packs in packages_required:
  cp.install(packs)

import pandas as pd
import requests
import os
import gc
import pickle

def download_file_from_url(url,folder_path):
    #Downloading the file into datasets folder
    filename = url.split("/")[-1]
    with open(folder_path+filename, "wb") as f:
        r = requests.get(url)
        f.write(r.content)
    print("File " + filename + " succesfully downloaded.")

def download_datasets(folder_path,url):
    #Creating datasets folder in case it doesn't exists
    if os.path.exists(folder_path) == False:
        print("Path folder didn't exists, we'll create it")
        os.makedirs(folder_path)

    filename = url.split("/")[-1]
    if os.path.isfile(folder_path + filename) == False:
        print("Downloading file " + filename)
        download_file_from_url(url,folder_path)
    else:
        print("File " + filename + " already in filesystem.")

def create_pickle_file(data_dict,path,logger):
    logger.debug(f'Creating pickle file at {path}.')
    with open(path, 'wb') as handle:
        pickle.dump(data_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    logger.debug(f'Pickle file created at {path}.')

def read_pickle_file(path,logger):
    logger.debug(f'Reading pickle file at {path}.')
    with open(path, 'rb') as handle:
        data_dict = pickle.load(handle)
    logger.debug(f'Pickle file read at {path}.')
    return data_dict