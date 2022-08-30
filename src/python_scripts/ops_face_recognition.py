import os
import re
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC

from ops_logger import create_logger, shutdown_logger
from ops_files_operations import create_pickle_file, get_latest_model_name, read_json_file, read_pickle_file,add_recognizer_path_to_model
import ops_face_detection as fd

def train_recognizer(embeddings_folder, model_name = None, C=1.0, kernel='linear', probability=True, logger = None):
    if logger is None:
        close_logger = True
        logger = create_logger(script_name = 'autolog_' + os.path.basename(__name__))
    else:
        close_logger = False

    embeddings_index_file = os.path.join(embeddings_folder,'embeddings_metadata.json')
    embeddings_index = read_json_file(embeddings_index_file, logger = logger)

    if model_name is None:
        logger.debug(f'No model name provided. Using latest model.')
        model_name = get_latest_model_name(embeddings_index_file, logger = logger)
        if model_name == 'embeddings_0':
          logger.info(f'No model found, could not create recognizer.')
          return

    model_data = [item for item in embeddings_index if item.get('model_name')==model_name]

    logger.info(f'Creating recognizer for model {model_name}.')
    embeddings_data = read_pickle_file(model_data[0]['embeddings_path'],logger = logger)
    le = LabelEncoder()
    labels = le.fit_transform(embeddings_data["names"])
    embeddings = np.squeeze(np.array(embeddings_data["embeddings"]))
    le_name_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
    recognizer = SVC(C = C, kernel=kernel, probability=probability)
    recognizer.fit(embeddings, labels)
    recognizer_dict = {'recognizer': recognizer, 'le': le, 'le_name_mapping': le_name_mapping, 'model_name': model_name}
    logger.info(f'Recognizer created for model {model_name}.')

    if close_logger:
        shutdown_logger(logger)

    return recognizer_dict

def create_recognizer_model(recognizer_dict, recognizer_path,logger=None):
    if logger is None:
        close_logger = True
        logger = create_logger(script_name = 'autolog_' + os.path.basename(__name__))
    else:
        close_logger = False

    model_name = recognizer_dict['model_name']
    recognizer_name = model_name+'_recognizer.pickle'
    if os.path.isfile(os.path.join(recognizer_path,recognizer_name)) is True:
        logger.info(f'Recognizer {recognizer_name} already exists. Skipping creation.')
        if close_logger:
            shutdown_logger(logger)
        return

    recognizer_file = os.path.join(recognizer_path,recognizer_name)
    create_pickle_file(recognizer_dict,recognizer_file,logger = logger)
    add_recognizer_path_to_model(recognizer_file,model_name,logger = logger)

    if close_logger:
        shutdown_logger(logger)

def predict_probabilities(target_embeddings,embeddings_folder,recognizer_folder,array_format = False, model_name = None,logger = None):
    if logger is None:
        close_logger = True
        logger = create_logger(script_name = 'autolog_' + os.path.basename(__name__))
    else:
        close_logger = False

    if model_name is None:
        logger.debug(f'No model name provided. Using latest model.')
        embeddings_index_file = 'embeddings_metadata.json'
        model_name = get_latest_model_name(os.path.join(embeddings_folder,embeddings_index_file), logger = logger)
        if model_name == 'embeddings_0':
          logger.info(f'No model found, could not predict probabilities.')
          return

    recognizer_name = model_name+'_recognizer.pickle'
    recognizer_path = os.path.join(recognizer_folder,recognizer_name)
    if os.path.isfile(recognizer_path) is False:
        logger.info(f'Recognizer {recognizer_name} does not exists, can not predict probabilities.')
        return

    recognizer = read_pickle_file(recognizer_path, logger = logger)
    target_embeddings = np.array(target_embeddings)
    predictions = recognizer['recognizer'].predict_proba(target_embeddings)[0]
    predictions_dict = dict(zip(recognizer['le'].classes_,predictions))
    sorted_predictions_dict = dict((x, y) for x, y in sorted(predictions_dict.items(), key=lambda x: x[1], reverse=True))

    logger.info(f'Probabilities predicted with model {model_name} for given embeddings.')
    if close_logger:
        shutdown_logger(logger)

    if array_format:
        return np.array(list(sorted_predictions_dict.items()))
    else:
        return sorted_predictions_dict