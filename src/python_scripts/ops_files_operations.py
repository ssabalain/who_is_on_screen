from ops_check_packages import install_packages
ops_files_operations_packages = ["pandas","requests"]
install_packages(ops_files_operations_packages)

import pandas as pd
import requests
import os
import gc
import pickle
import json

from ops_logger import Logger

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

def create_pickle_file(data_dict,path,logger=None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

    if os.path.exists(os.path.dirname(path)) == False:
        logger.debug(f'Path {os.path.dirname(path)} doesn\'t exist, we will create it.')
        os.makedirs(os.path.dirname(path))

    logger.debug(f'Creating pickle file at {path}.')
    with open(path, 'wb') as handle:
        pickle.dump(data_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    handle.close()
    logger.debug(f'Pickle file created at {path}.')

    if close_logger:
        log.shutdown_logger()

def read_pickle_file(path,logger = None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

    logger.debug(f'Reading pickle file at {path}.')
    with open(path, 'rb') as handle:
        data_dict = pickle.load(handle)
    handle.close()
    logger.debug(f'Pickle file read at {path}.')

    if close_logger:
        log.shutdown_logger()

    return data_dict

def create_json_file(data_dict,path,logger=None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

    if os.path.exists(os.path.dirname(path)) == False:
        logger.debug(f'Path {os.path.dirname(path)} doesn\'t exist, we will create it.')
        os.makedirs(os.path.dirname(path))

    logger.debug(f'Creating json file at {path}.')
    with open(path,'w') as json_file:
        json.dump(data_dict, json_file, indent=4, separators=(',',': '))
    json_file.close()
    logger.debug(f'Json file created at {path}.')

    if close_logger:
        log.shutdown_logger()

def read_json_file(path,logger=None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

    logger.debug(f'Reading json file at {path}.')
    with open(path) as json_file:
        data_dict = json.load(json_file)
    json_file.close()
    logger.debug(f'Json file read at {path}.')

    if close_logger:
        log.shutdown_logger()

    return data_dict

def get_element_from_metadata(metadata_file_path,key=None,value=None,latest=False,logger=None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

    try:
        file_name = metadata_file_path.split(os.path.sep)[-1]
        logger.debug(f'Reading {file_name}.')
        if os.path.isfile(metadata_file_path) is False:
            logger.debug(f"File {file_name} doesn't exist")
            return
        else:
            metadata_array = read_json_file(metadata_file_path,logger)
            if key is not None and value is not None:
                logger.debug(f'Grabbing element with {key} = {value} for file {file_name}.')
                matching_array = []
                for element in metadata_array:
                    if key in element:
                        if element[key] == value:
                            matching_array.append(element)

                if len(matching_array) == 0:
                    logger.debug(f'No elements with {key} = {value} were found')
                    return
                elif len(matching_array) == 1:
                    logger.debug(f'One element with {key} = {value} was found, returning it.')
                    return matching_array[0]
                else:
                    logger.debug(f'{len(matching_array)} elements with {key} = {value} were found.')
                    if latest == True:
                        logger.debug(f'Returning the latest element.')
                        return matching_array[-1]
                    else:
                        logger.debug(f'Returning first element.')
                        return matching_array[0]
            else:
                if latest == True:
                    logger.debug(f'Returning the latest element.')
                    return metadata_array[-1]
                else:
                    logger.debug(f'Not enough data to proceed.')
                    return
    finally:
        if close_logger:
            log.shutdown_logger()

def add_dict_to_metadata_file(path,dict,logger = None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

    if os.path.isfile(path) is False:
        logger.debug(f'File {path.split(os.path.sep)[-1]} doesnt exist, we will create it.')
        dict_array=[]
        dict_array.append(dict)
    else:
        logger.debug(f'File {path.split(os.path.sep)[-1]} already exist.')
        dict_array = read_json_file(path,logger)
        dict_array.append(dict)

    create_json_file(dict_array,path,logger)

    if close_logger:
        log.shutdown_logger()

def add_recognizer_path_to_model(recognizer_id,model_id,logger=None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

    model_index_path = './models/embeddings/actor_faces/models_metadata.json'

    logger.debug(f'Adding recognizer path to model {model_id}.')
    model_index = read_json_file(model_index_path,logger=logger)
    for models in model_index:
        if models['model_id'] == model_id:
            if 'recognizer_id' in models.keys():
                models['recognizer_id'].append(recognizer_id)
            else:
                models['recognizer_id'] = [recognizer_id]
            break

    create_json_file(model_index,model_index_path,logger)
    logger.debug(f'Recognizer path succesfully added to model {model_id}.')

    if close_logger:
        log.shutdown_logger()