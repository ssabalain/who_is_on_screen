# from ops_check_packages import install_packages
# ops_face_recognition_packages = ["pandas"]
# install_packages(ops_face_recognition_packages)

import os
import re
from time import time, strftime, localtime, gmtime
from random import randrange
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
import uuid
import statistics

from ops_logger import Logger
from ops_files_operations import create_pickle_file, read_pickle_file,\
    add_recognizer_path_to_model,add_dict_to_metadata_file,get_element_from_metadata
from ops_face_detection import get_actors_dict, get_actors_embeddings,get_embeddings_from_image

def train_recognizer(embeddings_dict=None,embeddings_metadata=None,embeddings_folder=None,model_id=None,kernel='linear',C=1.0,gamma=1.0,degree=2,probability=True,save_to_pickle=False,output_folder=None, logger=None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

    try:
        process_start = time()
        if embeddings_dict is None:
            if embeddings_folder is None:
                logger.info(f'No embeddings provided, can not train recognizer.')
                return
            else:
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

                logger.debug(f'Creating recognizer for model {model_id}.')
                embeddings_data = read_pickle_file(model_dict['pickle_path'],logger=logger)
        else:
            if embeddings_metadata is None:
                logger.info(f'No embeddings metadata provided, can not train recognizer.')
                return
            logger.debug(f'Creating recognizer for given embeddings.')
            embeddings_data = embeddings_dict
            model_id = embeddings_metadata['model_id']

        le = LabelEncoder()
        labels = le.fit_transform(embeddings_data["names"])
        embeddings = np.squeeze(np.array(embeddings_data["embeddings"]))
        le_name_mapping = dict(zip(le.classes_, le.transform(le.classes_)))

        if kernel == 'linear':
            recognizer = SVC(
                kernel=kernel,
                C=C,
                probability=probability
            )
        elif kernel == 'rbf':
            recognizer = SVC(
                kernel=kernel,
                C=C,
                gamma=gamma,
                probability=probability
            )
        elif kernel == 'poly':
            recognizer = SVC(
                kernel=kernel,
                C=C,
                degree=degree,
                probability=probability
            )
        else:
            logger.info(f'Kernel {kernel} not supported.')
            return None, None

        recognizer.fit(embeddings, labels)

        process_end = time()
        process_time = str(process_end - process_start)
        recognizer_dict = {'recognizer': recognizer, 'le': le, 'le_name_mapping': le_name_mapping}
        recognizer_metadata = {
            "recognizer_id": str(uuid.uuid4()),
            "execution_timestamp": strftime('%Y-%m-%d %H:%M:%S', localtime(process_start)),
            "process_time": process_time,
            "model_id": model_id,
            "kernel": kernel,
            "C": C,
            "gamma": gamma,
            "degree": degree,
            "probability": probability,
            "pickle_path": ""
        }

        logger.debug(f'Recognizer created for model {model_id}.')
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
            log.shutdown_logger()

def predict_probabilities(target_embeddings,recognizer_folder=None,recognizer=None,recognizer_metadata=None,array_format=False,recognizer_id=None,logger=None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

    try:
        if target_embeddings is not None and len(target_embeddings) == 1:
            if len(target_embeddings[0]) == 128:
                target_embeddings = np.array(target_embeddings)
            else:
                logger.debug("Embedding is not suitable for predicting.")
                return None, None
        else:
            logger.debug("Embedding is not suitable for predicting.")
            return None, None

        if recognizer_folder is not None:
            model_index_path = './models/recognizers/recognizer_metadata.json'
            if recognizer_id is None:
                logger.debug(f'No recognizer_id provided. Using latest model.')
                model_dict = get_element_from_metadata(model_index_path, latest=True, logger=logger)
                if model_dict is None:
                    logger.info(f'No model found, could not predict probabilities.')
                    return None, None
                recognizer_id = model_dict['recognizer_id']

            recognizer_index_file = 'recognizer_metadata.json'
            recognizer_index_path = os.path.join(recognizer_folder,recognizer_index_file)
            recognizer_metadata = get_element_from_metadata(recognizer_index_path,key='recognizer_id',value=recognizer_id,latest=True,logger=logger)
            recognizer_path = recognizer_metadata['pickle_path']

            if os.path.isfile(recognizer_path) is False:
                logger.info(f'Recognizer {recognizer_id} does not exists, can not predict probabilities.')
                return None, None

            recognizer = read_pickle_file(recognizer_path, logger=logger)
        else:
            if recognizer is None or recognizer_metadata is None:
                logger.info(f'No recognizer provided, can not predict probabilities.')
                return None, None
            recognizer_id = recognizer_metadata['recognizer_id']

        predictions = recognizer['recognizer'].predict_proba(target_embeddings)[0]
        predictions_dict = dict(zip(recognizer['le'].classes_,predictions))
        sorted_predictions_dict = dict((x, y) for x, y in sorted(predictions_dict.items(), key=lambda x: x[1], reverse=True))

        logger.debug(f'Probabilities predicted with recognizer {recognizer_id} for given embeddings.')
        if array_format:
            return np.array(list(sorted_predictions_dict.items())), recognizer_metadata['recognizer_id']
        else:
            return sorted_predictions_dict, recognizer_metadata['recognizer_id']

    finally:
        if close_logger:
            log.shutdown_logger()

def get_probabilities_for_file(pickle_file_path, recognizer_folder=None,recognizer=None,recognizer_metadata=None,recognizer_id=None,logger=None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

    target_embeddings_array = read_pickle_file(pickle_file_path, logger=logger)
    file_probabilities = []

    for frames in target_embeddings_array:
        frame_predictions = []
        for embedding in frames[2][0]:
            prob_dict, recognizer_id = predict_probabilities([embedding],recognizer_folder,recognizer,recognizer_metadata,recognizer_id=recognizer_id,logger=logger)
            frame_predictions.append(prob_dict)

        frame_results = {
            "frame_number": frames[0],
            "timestamp": frames[1],
            "predictions": frame_predictions
        }

        file_probabilities.append(frame_results)

    if close_logger:
        log.shutdown_logger()

    return file_probabilities, recognizer_id

def get_probabilities_for_folder(folder_path, recognizer_folder,save_to_pickle=False,output_folder=None,processed_video_id=None, recognizer_id=None, logger=None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
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
            chunk_probabilities, recognizer_id = get_probabilities_for_file(chunk_path, recognizer_folder=recognizer_folder, recognizer_id=recognizer_id, logger=logger)
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
            log.shutdown_logger()

def get_pipeline_results(faces_folder,seed=None,test_sample=None,kernel=None,C=None,gamma=None,degree=None,logger=None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

    try:
        logger.debug(f'Getting pipeline results.')
        train_dict,test_dict= get_actors_dict(faces_folder,test_sample,seed,logger=logger)
        emb_dict, metadata_dict = get_actors_embeddings(faces_folder,test_sample,seed,logger=logger)
        recognizer_dict, recognizer_metadata = train_recognizer(
            embeddings_dict=emb_dict,
            embeddings_metadata=metadata_dict,
            kernel=kernel,
            C=C,
            gamma=gamma,
            degree=degree,
            logger=logger
        )

        pipeline_dict= {
            "seed": seed,
            "test_sample": test_sample,
            "kernel":kernel,
            "C": C,
            "gamma": gamma,
            "degree": degree,
            "avg_accuracy": 0,
            "avg_accuracy_top3": 0,
            "results_dict": {}
        }
        accuracy_array = []
        top3_array = []

        for actor in test_dict:
            logger.debug(f'Predicting probabilities for actor {actor}')
            pipeline_dict["results_dict"][actor] = {}
            total_images=0
            total_hits=0
            total_top3=0
            for path in test_dict[actor]:
                try:
                    img_embeddings, img_metadata = get_embeddings_from_image(img_path = path)
                    predictions, recognizer_id = predict_probabilities(img_embeddings,recognizer=recognizer_dict,recognizer_metadata=recognizer_metadata,array_format = True)
                except:
                    predictions = None
                    logger.debug(f'Could not get embeddings for image {path}')

                if predictions is not None:
                    logger.debug(f'Predictions obtained for path {path}')
                    total_images+=1
                    if actor == predictions[0][0]:
                        total_hits+=1
                    for prediction in predictions[0:3]:
                        if actor == prediction[0]:
                            total_top3+=1
                            break

            logger.debug(f'{total_images} predicted for actor {actor}. Accuracy is {total_hits/total_images}. Top 3 accuracy is {total_top3/total_images}')
            pipeline_dict["results_dict"][actor]["total_images"] = total_images
            pipeline_dict["results_dict"][actor]["total_hits"] = total_hits
            pipeline_dict["results_dict"][actor]["total_top3"] = total_top3
            pipeline_dict["results_dict"][actor]["accuracy"] = total_hits/total_images
            pipeline_dict["results_dict"][actor]["accuracy_top3"] = total_top3/total_images
            accuracy_array.append(total_hits/total_images)
            top3_array.append(total_top3/total_images)

        pipeline_dict["avg_accuracy"] = statistics.mean(accuracy_array)
        pipeline_dict["avg_accuracy_top3"] = statistics.mean(top3_array)
        logger.debug(f'Pipeline results obtained. Average accuracy is {pipeline_dict["avg_accuracy"]}. Average top 3 accuracy is {pipeline_dict["avg_accuracy_top3"]}')
        return pipeline_dict

    finally:
        if close_logger:
            log.shutdown_logger()

def train_pipelines(faces_folder,test_sample,kernels,C_values,gammas,degrees,iterations,save_to_pickle=False,output_folder=None,logger=None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

    try:
        process_start = time()
        pipelines = []
        keys= ['parameters_uuid','seed','test_sample','C','gamma','degree','kernel','avg_accuracy','avg_accuracy_top3']

        for kernel in kernels:
            logger.debug(f'Training pipelines for kernel = {kernel}')
            if kernel == 'linear':
                for C in C_values:
                    logger.debug(f'Training pipelines for C = {C}')
                    parameters_uuid = str(uuid.uuid4())
                    for iteration in range(iterations):
                        seed = randrange(10000)
                        logger.debug(f'Training pipeline for iteration {iteration} with seed {seed}')
                        pipeline_results = get_pipeline_results(
                                faces_folder=faces_folder,
                                seed=seed,
                                test_sample=test_sample,
                                kernel=kernel,
                                C=C
                            )
                        pipeline_results["parameters_uuid"] = parameters_uuid
                        pipelines.append({ key:pipeline_results[key] for key in keys})
                        logger.debug(f'Pipeline trained. Average accuracy is {pipeline_results["avg_accuracy"]}. Average top 3 accuracy is {pipeline_results["avg_accuracy_top3"]}')
            elif kernel == 'rbf':
                for G in gammas:
                    logger.debug(f'Training pipelines for gamma = {G}')
                    for C in C_values:
                        logger.debug(f'Training pipelines for C = {C}')
                        parameters_uuid = str(uuid.uuid4())
                        for iteration in range(iterations):
                            seed = randrange(10000)
                            logger.debug(f'Training pipeline for iteration {iteration} with seed {seed}')
                            pipeline_results = get_pipeline_results(
                                faces_folder=faces_folder,
                                seed=seed,
                                test_sample=test_sample,
                                kernel=kernel,
                                C=C,
                                gamma=G
                            )
                            pipeline_results["parameters_uuid"] = parameters_uuid
                            pipelines.append({ key:pipeline_results[key] for key in keys})
                            logger.debug(f'Pipeline trained. Average accuracy is {pipeline_results["avg_accuracy"]}. Average top 3 accuracy is {pipeline_results["avg_accuracy_top3"]}')
            elif kernel == 'poly':
                for degree in degrees:
                    logger.debug(f'Training pipelines for degree = {degree}')
                    for C in C_values:
                        logger.debug(f'Training pipelines for C = {C}')
                        parameters_uuid = str(uuid.uuid4())
                        for iteration in range(iterations):
                                seed = randrange(10000)
                                logger.debug(f'Training pipeline for iteration {iteration} with seed {seed}')
                                pipeline_results = get_pipeline_results(
                                    faces_folder=faces_folder,
                                    seed=seed,
                                    test_sample=test_sample,
                                    kernel=kernel,
                                    C=C,
                                    degree=degree
                                )
                                pipeline_results["parameters_uuid"] = parameters_uuid
                                pipelines.append({ key:pipeline_results[key] for key in keys})
                                logger.debug(f'Pipeline trained. Average accuracy is {pipeline_results["avg_accuracy"]}. Average top 3 accuracy is {pipeline_results["avg_accuracy_top3"]}')

        logger.debug(f'Pipelines trained. Obtained {len(pipelines)} pipelines')
        process_end = time()
        process_time = str(process_end - process_start)
        pipelines_metadata = {
            "pipelines_id": str(uuid.uuid4()),
            "execution_timestamp": strftime('%Y-%m-%d %H:%M:%S', localtime(process_start)),
            "process_time": process_time,
            "test_sample": test_sample,
            "kernels": kernels,
            "C_values": C_values,
            "gammas": gammas,
            "degrees": degrees,
            "iterations": iterations
        }

        if save_to_pickle is True:
            if output_folder is None:
                logger.debug(f'No output folder provided. Please provide one')
                return

            logger.debug(f'Saving pipelines to pickle file.')
            pipelines_file = os.path.join(output_folder, 'pipelines_' + pipelines_metadata["pipelines_id"] + '.pickle')
            create_pickle_file(pipelines, pipelines_file,logger=logger)
            pipelines_metadata["pickle_path"] = pipelines_file
            pipelines_metadata_file = os.path.join(output_folder, 'pipelines_metadata.json')
            add_dict_to_metadata_file(pipelines_metadata_file,pipelines_metadata,logger=logger)

        return pipelines, pipelines_metadata

    finally:
        if close_logger:
            log.shutdown_logger()