import ops_check_packages as cp

packages_required = ["pandas","requests"]

for packs in packages_required:
  cp.install(packs)

import pandas as pd
import requests
import os
import gc

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