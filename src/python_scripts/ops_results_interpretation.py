import logging
from ops_check_packages import install_packages
ops_results_interpretation_packages = ["pandas","pandasql","matplotlib"]
install_packages(ops_results_interpretation_packages)

import os
import json
import pandas as pd
import numpy as np
from pandasql import sqldf
import matplotlib.pyplot as plt
from time import time, strftime, localtime, gmtime

from ops_logger import Logger
from ops_files_operations import read_pickle_file, read_json_file, get_element_from_metadata

def get_frames_df(processed_videos_metadata,logger=None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

    try:
        frames = {'frame_number': [], 'timestamp': []}
        if processed_videos_metadata is None:
            logger.debug('No processed video metadata passed.')
            return None

        total_frames = int(processed_videos_metadata['total_frames'])
        desired_fps = int(processed_videos_metadata['desired_fps'])
        video_fps = float(processed_videos_metadata['video_fps'])
        for i in range(0,total_frames,desired_fps):
            if i == 0:
                    frames['frame_number'].append(1)
                    frames['timestamp'].append('00.00:00.000')
            else:
                frames['frame_number'].append(i)
                frames['timestamp'].append(strftime('%H:%M:%S.{}'.format(round(round((i/video_fps) % 1,3)*1000)), gmtime(i/video_fps)))
        frames_df = pd.DataFrame(frames)
        logger.debug('Frames dataframe created.')
        return(frames_df)

    finally:
        if close_logger:
            log.shutdown_logger()

def get_actors_probs_query(actor_name, filtering_statement = True, logger=None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

    try:
        logger.debug(f'Creating query for actor {actor_name}.')
        fd = open('./python_scripts/support_files/probs_for_actor_query.sql', 'r')
        sqlFile = fd.read().format(actor_name,filtering_statement)
        fd.close()
        return(sqlFile)

    finally:
        if close_logger:
            log.shutdown_logger()

def get_predicted_timeline(results_id,avoid_nulls = True, only_boundaries = True, logger=None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

    try:
        if results_id is None:
            logger.debug('No results id passed.')
            return None

        results_metadata_path = './models/results/probabilities_metadata.json'
        processed_videos_metadata_path = './models/embeddings/processed_videos/the_final_kick/processed_videos_metadata.json'

        results_metadata = get_element_from_metadata(
            metadata_file_path=results_metadata_path,
            key = 'results_id',
            value = results_id,
            latest=True,
            logger=logger
        )
        pickle_path = results_metadata['pickle_path']
        results = read_pickle_file(pickle_path, logger=logger)

        logger.debug('Getting full probs df.')
        full_probs = []
        for chunk in results:
            for preds in chunk["probabilities"]:
                preds_dict= {}
                preds_dict["frame_number"] = preds["frame_number"]
                preds_dict["timestamp"] = preds["timestamp"]
                preds_dict["pred_1_name"] = sorted(preds["predictions"][0], key=preds["predictions"][0].get, reverse=True)[0]
                preds_dict["pred_1_value"] = preds["predictions"][0][preds_dict["pred_1_name"]]
                preds_dict["pred_2_name"] = sorted(preds["predictions"][0], key=preds["predictions"][0].get, reverse=True)[1]
                preds_dict["pred_2_value"] = preds["predictions"][0][preds_dict["pred_2_name"]]
                preds_dict["pred_3_name"] = sorted(preds["predictions"][0], key=preds["predictions"][0].get, reverse=True)[2]
                preds_dict["pred_3_value"] = preds["predictions"][0][preds_dict["pred_3_name"]]
                full_probs.append(preds_dict)

        results_df = pd.DataFrame(full_probs)

        processed_videos_metadata = get_element_from_metadata(
            metadata_file_path = processed_videos_metadata_path,
            key = 'processed_video_id',
            value = results_metadata['processed_video_id'],
            logger = logger
        )

        frames_df = get_frames_df(processed_videos_metadata, logger=logger)
        all_actor_probs = pd.DataFrame(columns=['actor','frame_number','timestamp','pred_value','is_start','is_end'])
        if only_boundaries:
                filter_statement = '(is_start or is_end = 1)'
        elif avoid_nulls:
                filter_statement = 'pred_value != 0'
        else:
                filter_statement = 'true'

        for actor in results[0]['probabilities'][0]['predictions'][0].keys():
            logger.debug(f'Getting probs for actor {actor}.')
            actor_probs_query = get_actors_probs_query(actor, filtering_statement=filter_statement, logger=logger)
            actors_probs = sqldf(str(actor_probs_query))
            all_actor_probs = pd.concat([all_actor_probs,actors_probs], ignore_index=True)

        return(all_actor_probs)

    finally:
        if close_logger:
            log.shutdown_logger()

def get_summarized_timeline(results_id,logger=None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

    try:
        logger.debug('Getting the two timelines.')
        full_timeline = get_predicted_timeline(results_id, avoid_nulls = False, only_boundaries = False, logger=logger)
        short_timeline = get_predicted_timeline(results_id, logger=logger)

        fd = open('./python_scripts/support_files/summarized_probs_query.sql', 'r')
        summarized_query = fd.read()
        fd.close()

        summarized_df = sqldf(str(summarized_query))
        return(summarized_df)

    finally:
        if close_logger:
            log.shutdown_logger()