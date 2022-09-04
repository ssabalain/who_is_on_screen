import os
import re
from time import time, strftime, localtime, gmtime
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
import uuid

from ops_logger import create_logger, shutdown_logger
from ops_files_operations import create_pickle_file, read_pickle_file,\
    add_recognizer_path_to_model,add_dict_to_metadata_file,get_element_from_metadata
import ops_face_detection as fd

def train_recognizer(embeddings_folder, model_id=None, C=1.0, kernel='linear', probability=True, save_to_pickle=False,output_folder=None, logger=None):
    if logger is None:
        close_logger = True
        logger = create_logger(script_name = 'autolog_' + os.path.basename(__name__))
    else:
        close_logger = False

    try:
        process_start = time()
        model_index_file = os.path.join(embeddings_folder,'models_metadata.json')

        if model_id is None:
            logger.debug(f'No model id provided. Using latest model.')
            model_dict = get_element_from_metadata(model_index_file, latest=True,logger=logger)
            if model_dict is None:
                logger.info(f'No model found, could not create recognizer.')
                return
            model_id = model_dict['model_id']
        else:
            model_dict = get_element_from_metadata(model_index_file,key='model_id',value=model_id,latest=True,logger=logger)
            if model_dict is None:
                logger.info(f'No model found, could not create recognizer.')
                return

        logger.info(f'Creating recognizer for model {model_id}.')
        embeddings_data = read_pickle_file(model_dict['pickle_path'],logger=logger)
        le = LabelEncoder()
        labels = le.fit_transform(embeddings_data["names"])
        embeddings = np.squeeze(np.array(embeddings_data["embeddings"]))
        le_name_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
        recognizer = SVC(C=C, kernel=kernel, probability=probability)
        recognizer.fit(embeddings, labels)

        process_end = time()
        process_time = str(process_end - process_start)
        recognizer_dict = {'recognizer': recognizer, 'le': le, 'le_name_mapping': le_name_mapping}
        recognizer_metadata = {
            "recognizer_id": str(uuid.uuid4()),
            "execution_timestamp": strftime('%Y-%m-%d %H:%M:%S', localtime(process_start)),
            "process_time": process_time,
            "model_id": model_id,
            "C": C,
            "kernel": kernel,
            "probability": probability,
            "pickle_path": ""
        }

        logger.info(f'Recognizer created for model {model_id}.')
        if save_to_pickle is True:
            if output_folder is None:
                logger.debug(f'No output folder provided. Please provide one')
                return

            logger.debug(f'Saving recognizer to pickle file.')
            recognizer_file = os.path.join(output_folder, 'recognizer_' + recognizer_metadata["recognizer_id"] + '.pickle')
            create_pickle_file(recognizer_dict, recognizer_file,logger=logger)
            recognizer_metadata["pickle_path"] = recognizer_file
            recognizer_metadata_file = os.path.join(output_folder, 'recognizer_metadata.json')
            add_dict_to_metadata_file(recognizer_metadata_file,recognizer_metadata,logger=logger)
            add_recognizer_path_to_model(recognizer_metadata["recognizer_id"],model_id,logger=logger)

        return recognizer_dict, recognizer_metadata

    finally:
        if close_logger:
            shutdown_logger(logger)

def predict_probabilities(target_embeddings,recognizer_folder,array_format = False, model_id=None,logger=None):
    if logger is None:
        close_logger = True
        logger = create_logger(script_name = 'autolog_' + os.path.basename(__name__))
    else:
        close_logger = False

    try:
        recognizer_index_file = 'recognizer_metadata.json'
        recognizer_index_path = os.path.join(recognizer_folder,recognizer_index_file)
        model_index_path = './models/embeddings/actor_faces/models_metadata.json'

        if model_id is None:
            logger.debug(f'No model name provided. Using latest model.')
            model_dict = get_element_from_metadata(model_index_path, latest=True, logger=logger)
            if model_dict is None:
                logger.info(f'No model found, could not predict probabilities.')
                return
            model_id = model_dict['model_id']

        recognizer_dict = get_element_from_metadata(recognizer_index_path,key='model_id',value=model_id,latest=True,logger=logger)
        recognizer_path = recognizer_dict['pickle_path']

        if os.path.isfile(recognizer_path) is False:
            logger.info(f'Recognizer for model {model_id} does not exists, can not predict probabilities.')
            return

        recognizer = read_pickle_file(recognizer_path, logger = logger)
        target_embeddings = np.array(target_embeddings)
        predictions = recognizer['recognizer'].predict_proba(target_embeddings)[0]
        predictions_dict = dict(zip(recognizer['le'].classes_,predictions))
        sorted_predictions_dict = dict((x, y) for x, y in sorted(predictions_dict.items(), key=lambda x: x[1], reverse=True))

        logger.debug(f'Probabilities predicted with model {model_id} for given embeddings.')
        if array_format:
            return np.array(list(sorted_predictions_dict.items())), recognizer_dict['recognizer_id']
        else:
            return sorted_predictions_dict, recognizer_dict['recognizer_id']

    finally:
        if close_logger:
            shutdown_logger(logger)

def get_probabilities_for_file(pickle_file_path, recognizer_folder, model_id=None, logger=None):
    if logger is None:
        close_logger = True
        logger = create_logger(script_name = 'autolog_' + os.path.basename(__name__))
    else:
        close_logger = False

    target_embeddings_array = read_pickle_file(pickle_file_path, logger=logger)
    file_probabilities = []

    for frames in target_embeddings_array:
        frame_predictions = []
        for embedding in frames[2][0]:
            prob_dict, recognizer_id = predict_probabilities([embedding],recognizer_folder, model_id=model_id, logger=logger)
            frame_predictions.append(prob_dict)

        frame_results = {
            "timestamp": frames[1],
            "predictions": frame_predictions
        }

        file_probabilities.append(frame_results)

    if close_logger:
        shutdown_logger(logger)

    return file_probabilities, recognizer_id

def get_probabilities_for_folder(folder_path, recognizer_folder,save_to_pickle=False,output_folder=None,processed_video_id=None, model_id=None, logger=None):
    if logger is None:
        close_logger = True
        logger = create_logger(script_name = 'autolog_' + os.path.basename(__name__))
    else:
        close_logger = False

    try:
        process_start = time()
        folders_metadata_file = os.path.join(folder_path,'processed_videos_metadata.json')
        if processed_video_id is None:
            logger.debug(f'No processed_video_id provided. Using latest id.')
            folders_dict = get_element_from_metadata(folders_metadata_file,latest=True,logger=logger)
            processed_video_id = folders_dict['processed_video_id']
        else:
            folders_dict = get_element_from_metadata(folders_metadata_file,key='processed_video_id',value=processed_video_id,logger=logger)

        folder_probabilities_metadata = {
            "results_id": str(uuid.uuid4()),
            "processed_video_id": processed_video_id,
            "recognizer_id": None,
            "execution_timestamp": strftime('%Y-%m-%d %H:%M:%S', localtime(process_start)),
            "process_time": "",
            "pickle_path": "",
        }

        folder_probabilities = []

        for chunk in folders_dict["chunks"]:
            chunk_path = chunk["chunk_file"]
            chunk_probabilities, recognizer_id = get_probabilities_for_file(chunk_path, recognizer_folder=recognizer_folder, model_id=model_id, logger=logger)
            chunk_dict = {
                "chunk_no": chunk["chunk"],
                "probabilities": chunk_probabilities
            }
            folder_probabilities.append(chunk_dict)
            folder_probabilities_metadata["recognizer_id"] = recognizer_id

        process_end = time()
        folder_probabilities_metadata["process_time"] = str(process_end - process_start)

        if save_to_pickle is True:
            if output_folder is None:
                logger.debug(f'No output folder provided. Please provide one')
                return

            logger.debug(f'Saving probabilities to pickle file.')
            probabilities_file = os.path.join(output_folder, 'probabilities_' + folder_probabilities_metadata["results_id"] + '.pickle')
            create_pickle_file(folder_probabilities, probabilities_file,logger=logger)
            folder_probabilities_metadata["pickle_path"] = probabilities_file
            folder_probabilities_metadata_file = os.path.join(output_folder, 'probabilities_metadata.json')
            add_dict_to_metadata_file(folder_probabilities_metadata_file,folder_probabilities_metadata,logger=logger)

        return folder_probabilities, folder_probabilities_metadata

    finally:
        if close_logger:
            shutdown_logger(logger)