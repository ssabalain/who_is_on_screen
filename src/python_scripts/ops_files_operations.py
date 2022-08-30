from ops_check_packages import install_packages
ops_files_operations_packages = ["pandas","requests"]
install_packages(ops_files_operations_packages)

import pandas as pd
import requests
import os
import gc
import pickle
import json

from ops_logger import create_logger,shutdown_logger

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

def create_pickle_file(data_dict,path,logger = None):
    if logger is None:
        close_logger = True
        logger = create_logger(script_name = 'autolog_' + os.path.basename(__name__))
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
        shutdown_logger(logger)

def read_pickle_file(path,logger = None):
    if logger is None:
        close_logger = True
        logger = create_logger(script_name = 'autolog_' + os.path.basename(__name__))
    else:
        close_logger = False

    logger.debug(f'Reading pickle file at {path}.')
    with open(path, 'rb') as handle:
        data_dict = pickle.load(handle)
    handle.close()
    logger.debug(f'Pickle file read at {path}.')

    if close_logger:
        shutdown_logger(logger)

    return data_dict

def create_json_file(data_dict,path,logger=None):
    if logger is None:
        close_logger = True
        logger = create_logger(script_name = 'autolog_' + os.path.basename(__name__))
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
        shutdown_logger(logger)

def read_json_file(path,logger=None):
    if logger is None:
        close_logger = True
        logger = create_logger(script_name = 'autolog_' + os.path.basename(__name__))
    else:
        close_logger = False

    logger.debug(f'Reading json file at {path}.')
    with open(path) as json_file:
        data_dict = json.load(json_file)
    json_file.close()
    logger.debug(f'Json file read at {path}.')

    if close_logger:
        shutdown_logger(logger)

    return data_dict

def get_latest_model_name(path,logger = None):
    if logger is None:
        close_logger = True
        logger = create_logger(script_name = 'autolog_' + os.path.basename(__name__))
    else:
        close_logger = False

    logger.debug(f'Reading {path}.')
    if os.path.isfile(path) is False:
        logger.debug(f"File {path.split(os.path.sep)[-1]} doesn't exist, we initialize the embeddings files names")
        file_name = 'embeddings_0'
    else:
        logger.debug(f'File {path.split(os.path.sep)[-1]} already exist, we grab the latest embeddings file name')
        embeddings_array = read_json_file(path,logger)
        file_name = embeddings_array[-1]["model_name"]
        logger.debug(f'Returning file name "{file_name}"')

    if close_logger:
        shutdown_logger(logger)

    return(file_name)

def add_embeddings_data(path,embeddings_dict,logger = None):
    if logger is None:
        close_logger = True
        logger = create_logger(script_name = 'autolog_' + os.path.basename(__name__))
    else:
        close_logger = False

    if os.path.isfile(path) is False:
        logger.debug(f'File {path.split(os.path.sep)[-1]} doesnt exist, we will create it.')
        embeddings_array=[]
        embeddings_array.append(embeddings_dict)
    else:
        logger.debug(f'File {path.split(os.path.sep)[-1]} already exist.')
        embeddings_array = read_json_file(path,logger)
        embeddings_array.append(embeddings_dict)

    create_json_file(embeddings_array,path,logger)

    if close_logger:
        shutdown_logger(logger)

def add_embeddings_model(index_file,embeddings,metadata,logger = None):
    if logger is None:
        close_logger = True
        logger = create_logger(script_name = 'autolog_' + os.path.basename(__name__))
    else:
        close_logger = False

    latest_model_name = get_latest_model_name(index_file,logger)
    model_name = '_'.join(latest_model_name.split('_')[:-1])+'_'+str(int(latest_model_name.split('_')[-1])+1)
    logger.info(f'Adding {model_name} data to {index_file.split(os.path.sep)[-1]}.')
    model_path = os.path.join(os.path.sep.join(index_file.split(os.path.sep)[:-1]),model_name+'.pickle')
    logger.debug(f'Creating pickle file for model "{model_name}".')
    create_pickle_file(embeddings,model_path,logger)

    model_dict = {
        'model_name': model_name,
        'embeddings_path': model_path
    }

    model_dict.update(metadata)
    add_embeddings_data(index_file,model_dict,logger)
    logger.info(f'{model_name} successfully added to {index_file.split(os.path.sep)[-1]}.')
    if close_logger:
        shutdown_logger(logger)

def add_recognizer_path_to_model(recognizer_path,model_name,logger = None):
    if logger is None:
        close_logger = True
        logger = create_logger(script_name = 'autolog_' + os.path.basename(__name__))
    else:
        close_logger = False

    model_index_path = './models/embeddings/actor_faces/embeddings_metadata.json'

    logger.debug(f'Adding recognizer path to model {model_name}.')
    model_index = read_json_file(model_index_path,logger)
    for models in model_index:
        if models['model_name'] == model_name:
            if 'recognizer_path' in models.keys():
                models['recognizer_path'].append(recognizer_path)
            else:
                models['recognizer_path'] = [recognizer_path]
            break

    create_json_file(model_index,model_index_path,logger)
    logger.debug(f'Recognizer path succesfully added to model {model_name}.')

    if close_logger:
        shutdown_logger(logger)