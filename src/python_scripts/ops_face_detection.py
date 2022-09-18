from ops_check_packages import install_packages
ops_face_detection_packages = ["imutils","opencv-python","matplotlib"]
install_packages(ops_face_detection_packages)

from imutils import paths
import numpy as np
import imutils
import cv2
import os
import matplotlib.pyplot as plt
from time import time, strftime, localtime, gmtime
from datetime import datetime
import imghdr
import uuid
import random

from ops_logger import Logger
from ops_files_operations import add_dict_to_metadata_file, create_pickle_file

#Set 'src' folder as the working directory
script_name = os.path.basename(__name__)
path_arr = os.getcwd().split(os.path.sep)
os.chdir(os.path.sep.join(path_arr[:path_arr.index('src')+1]))

def path_index(image_path):
    return int(image_path.split(os.path.sep)[-1].split('.')[0].split('_')[-1])

def get_actors_dict(actor_faces_folder,test_sample=0,seed=0,logger=None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

    image_paths = list(paths.list_images(actor_faces_folder))
    actors_dict = {}
    test_dict = {}
    train_dict= {}

    logger.debug(f'Building full actors dict from {actor_faces_folder} folder.')
    for (i, image_path) in enumerate(image_paths):
        actor_name = image_path.split(os.path.sep)[3]

        if actor_name not in actors_dict.keys():
            logger.debug(f'Adding actor {actor_name} to dict.')
            actors_dict[actor_name] = []

        logger.debug(f'Adding image {i} for actor {actor_name} on dict.')
        actors_dict[actor_name].append(image_path)

    logger.debug(f'Sorting images alphabetically.')
    for actor, actors_images in actors_dict.items():
        actors_images.sort(key = path_index)

    logger.debug(f'Setting seed to {seed}.')
    random.seed(seed)

    logger.debug(f'Building train and test dicts. Test sample: {test_sample}.')
    for actor in actors_dict:
        logger.debug(f'Building train and test dicts for actor {actor}.')
        total_actor_images = len(actors_dict[actor])
        test_images_number = round(total_actor_images*test_sample)
        logger.debug(f'Total actor images: {total_actor_images}. Test images number: {test_images_number}.')
        random_test_index = []
        for i in range(0,test_images_number):
            test_index = random.randint(0,total_actor_images)
            random_test_index.append(test_index)

        test_dict[actor] = []
        train_dict[actor] = []

        for idx,image in enumerate(actors_dict[actor]):
            if idx in random_test_index:
                test_dict[actor].append(image)
            else:
                train_dict[actor].append(image)

    if close_logger:
        log.shutdown_logger()

    return train_dict, test_dict

def get_embeddings_from_image(img_path=None,provided_image=None,opencv_dnn_model=None,embedder=None,multiple_faces=False, min_confidence=0.9, display=False,logger=None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

    try:
        if opencv_dnn_model is None:
            logger.debug('OpenCV DNN model not provided. Loading default model.')
            protoPath = './models/face_detector/deploy.prototxt'
            modelPath = './models/face_detector/res10_300x300_ssd_iter_140000.caffemodel'
            opencv_dnn_model = cv2.dnn.readNetFromCaffe(protoPath, modelPath)

        if embedder is None:
            logger.debug('Embedding model not provided. Loading default model.')
            embeddingPath = './models/face_detector/openface.nn4.small2.v1.t7'
            embedder = cv2.dnn.readNetFromTorch(embeddingPath)

        logger.debug(f'Starting face detection. Multiple faces: {multiple_faces}. Minimun confidence: {min_confidence}. Display mode: {display}')
        scanned_faces = 0
        emb_time = 0
        scan_time = 0
        embeddings = []

        if provided_image is None:
            if img_path is None:
                logger.error('No image provided.')
                return None,None
            else:
                admited_file_types = ['jpeg','png','webp',None]
                file_format = imghdr.what(img_path)

                if file_format not in admited_file_types:
                    raise ValueError('The image provided is not withing the admited file formats',file_format)
                image = cv2.imread(img_path)
        else:
            image = provided_image

        image = imutils.resize(image, width=600)
        h, w, _ = image.shape
        output_image = image.copy()
        logger.debug(f'Converting image to blob...')
        preprocessed_image = cv2.dnn.blobFromImage(image, scalefactor=1.0, size=(300, 300), mean=(104.0, 117.0, 123.0), swapRB=False, crop=False)

        opencv_dnn_model.setInput(preprocessed_image)

        logger.debug(f'Scanning image...')
        scan_start = time()
        results = opencv_dnn_model.forward()
        scan_end = time()
        scan_time = str(scan_end - scan_start)
        logger.debug(f'Scanning complete. Exec time: {scan_time} seconds.')

        i = np.argmax(results[0, 0, :, 2])
        iteration = 0
        face_confidence_array = []

        for face in results[0][0]:
            if not multiple_faces:
                if iteration != i:
                    continue

            iteration+=1
            face_confidence = face[2]

            if face_confidence > min_confidence:
                logger.debug(f'Scanning face {iteration}. Face confidence: {face_confidence}.')

                face_confidence_array.append(str(face_confidence))

                # compute the (x, y)-coordinates of the bounding box for the face
                box = face[3:7] * np.array([w, h, w, h])
                (x1, y1, x2, y2) = box.astype("int")

                # extract the face ROI and grab the ROI dimensions
                face_roi = image[y1:y2, x1:x2]
                (fH, fW) = face_roi.shape[:2]

                # ensure the face width and height are sufficiently large
                if fW < 20 or fH < 20:
                    logger.debug(f'Face {iteration} didnt meet minimun size requirements, we are moving to the next one.')
                    continue

                # construct a blob for the face ROI, then pass the blob through our face embedding model to obtain the 128-d quantification of the face
                faceBlob = cv2.dnn.blobFromImage(face_roi, 1.0 / 255, (96, 96), (0, 0, 0), swapRB=True, crop=False)
                embedder.setInput(faceBlob)

                logger.debug(f'Processing image {iteration}...')
                emb_start = time()
                vec = embedder.forward()
                emb_end = time()
                emb_time = str(emb_end - emb_start)
                logger.debug(f'Processing completed. Exec time : {emb_time} seconds.')

                embeddings.append(vec.flatten())
                scanned_faces+=1

                if display:
                    cv2.rectangle(output_image, pt1=(x1, y1), pt2=(x2, y2), color=(0, 255, 0), thickness=w//200)

        logger.debug(f'Scan completed. Total faces scanned: {str(scanned_faces)}.')

        if display:
            plt.figure(figsize=[20,20])
            plt.subplot(121);plt.imshow(image[:,:,::-1]);plt.title("Original Image");plt.axis('off');
            plt.subplot(122);plt.imshow(output_image[:,:,::-1]);plt.title("Output");plt.axis('off');

        embeddings_metadata = {
            "img_path": img_path,
            "scanned_faces":str(scanned_faces),
            "face_confidence":face_confidence_array,
            "scan_time":str(scan_time),
            "emb_time":str(emb_time)
        }

        return embeddings, embeddings_metadata

    finally:
        if close_logger:
            log.shutdown_logger()

def get_actors_embeddings(actor_faces_folder,test_sample=0,seed=0,save_to_pickle=False,output_folder=None,images_per_actor=None,logger=None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

    try:
        process_start = time()
        actors_dict,test_dict = get_actors_dict(actor_faces_folder,test_sample,seed,logger=logger)
        logger.debug(f'Totals actors retrieved: {len(actors_dict)}.')

        actors_names = []
        actors_embeddings = []
        metadata_dict = {
            "model_id": str(uuid.uuid4()),
            "execution_timestamp": strftime('%Y-%m-%d %H:%M:%S', localtime(process_start)),
            "process_time": "0",
            "total_actors": str(len(actors_dict)),
            "actors":[],
            "pickle_path": ""
        }

        for actor, actors_images in actors_dict.items():
            actor_info = {
                "name": actor,
                "total_images": "0",
                "images_processed": []
            }
            processed_images = 0
            if images_per_actor is None:
                images_per_actor = len(actors_images)

            logger.debug(f'Analyzing actor {actor}. Total images available: {len(actors_images)}. Images to process: {images_per_actor}')

            for (i, img_path) in enumerate(actors_images):
                if i + 1 > images_per_actor:
                    continue

                logger.debug(f'Getting embeddings for image {i+1}/{images_per_actor} for actor {actor}.')
                try:
                    img_embeddings, img_metadata = get_embeddings_from_image(img_path,logger = logger)
                except ValueError as err:
                    logger.error(err)
                    continue

                if len(img_embeddings) == 1:
                    if len(img_embeddings[0]) == 128:
                        processed_images+=1
                        actors_names.append(actor)
                        actors_embeddings.append(img_embeddings)
                        actor_info["images_processed"].append(img_metadata)

                else:
                    logger.debug("Embedding is not 128, so we skip it.")
                    continue

            actor_info["total_images"] = str(processed_images)
            metadata_dict["actors"].append(actor_info)
            logger.debug(f'{processed_images}/{images_per_actor} images for actor {actor} were processed.')
            images_per_actor = None

        emb_dict = {"embeddings": actors_embeddings, "names": actors_names}
        process_end = time()
        process_time = str(process_end - process_start)
        logger.debug(f'Embedding extraction finished. Exec time: {process_time}.')
        metadata_dict["process_time"] = str(process_time)

        if save_to_pickle is True:
            if output_folder is None:
                logger.debug(f'No output folder provided. Please provide one')
                return

            logger.debug(f'Saving embeddings to pickle file.')
            embeddings_file = os.path.join(output_folder, 'actor_faces_embeddings_' + metadata_dict["model_id"] + '.pickle')
            create_pickle_file(emb_dict, embeddings_file,logger=logger)
            metadata_dict["pickle_path"] = embeddings_file
            model_metadata_file = os.path.join(output_folder, 'models_metadata.json')
            add_dict_to_metadata_file(model_metadata_file,metadata_dict,logger=logger)

        return emb_dict, metadata_dict

    finally:
        if close_logger:
            log.shutdown_logger()

def process_video(video_path,desired_fps=1, starting_frame=0, ending_frame=None, logger=None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

    process_start = time()
    frames_read = 0
    frames_with_faces = 0
    results = []

    try:
        cap = cv2.VideoCapture(video_path)
    except ValueError as err:
        logger.error(err)
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    logger.debug(f'Video fps: {video_fps}, total frames: {total_frames}, desired fps: {desired_fps}, starting frame: {starting_frame}, ending frame: {ending_frame}.')

    frame_no = starting_frame
    if starting_frame != 0:
        if starting_frame > total_frames:
            logger.error(f'Starting frame {starting_frame} is greater than total frames {total_frames}.')
            return
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no-1)

    if ending_frame is None:
        ending_frame = total_frames

    while(cap.isOpened()):
        frame_exists, curr_frame = cap.read()
        if frame_exists and frame_no <= ending_frame:
            if frame_no % (round(video_fps/desired_fps)) == 0:
                try:
                    frames_read+=1
                    frame_timestamp = strftime('%H:%M:%S.{}'.format(round(round((frame_no/video_fps) % 1,3)*1000)), gmtime(frame_no/video_fps))
                    frame_embeddings = np.array(get_embeddings_from_image(provided_image=curr_frame, multiple_faces=True, logger=logger), dtype=object)
                    if int(frame_embeddings[1]["scanned_faces"]) > 0:
                        frames_with_faces+=1
                        results.append([str(frame_no),str(frame_timestamp),frame_embeddings])
                except ValueError as err:
                    logger.error(err)
                    return
        else:
            break

        frame_no += 1

    results_array = np.asarray(results, dtype=object)
    process_end = time()
    process_time = str(process_end - process_start)
    logger.info(f'Total execution time = {process_time} seconds. Total frames: {frames_read}')

    cap.release()
    cv2.destroyAllWindows()

    if close_logger:
        log.shutdown_logger()

    metadata_dict = {
        "starting_frame": str(starting_frame),
        "ending_frame": str(ending_frame),
        "frames_read": str(frames_read),
        "frames_with_faces": str(frames_with_faces),
        "execution_timestamp": strftime('%Y-%m-%d %H:%M:%S', localtime(process_start)),
        "process_time": str(process_time)
    }

    return results_array, metadata_dict

def get_video_embeddings(video_path, results_path, partitions=1, desired_fps=1,logger=None):
    if logger is None:
        close_logger = True
        log = Logger(script_name = 'autolog_' + os.path.basename(__name__))
        log.create_logger()
        logger = log.logger
    else:
        close_logger = False

    try:
        process_start = time()
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            video_fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            cv2.destroyAllWindows()
        except ValueError as err:
            logger.error(err)
            return

        chunks = []
        chunk_size = round(total_frames/partitions)
        for i in range(partitions):
            starting_frame = i*chunk_size
            ending_frame = (starting_frame + chunk_size) - 1
            if ending_frame > total_frames or partitions == 1:
                ending_frame = total_frames
            chunk = [starting_frame,ending_frame]
            chunks.append(chunk)

        video_name = video_path.split(os.path.sep)[-1].split('.')[0]
        execution_metadata = {
            "processed_video_id": str(uuid.uuid4()),
            "execution_timestamp": strftime('%Y-%m-%d %H:%M:%S', localtime(process_start)),
            "video_path": video_path,
            "total_frames": str(total_frames),
            "video_fps": str(video_fps),
            "desired_fps": str(desired_fps),
            "partitions": str(partitions),
            "chunks": []
        }

        for idx, chunk in enumerate(chunks):
            results, chunk_metadata = process_video(video_path,desired_fps=desired_fps, starting_frame=chunk[0], ending_frame=chunk[1], logger=logger)
            chunk_name = video_name + '_' + str(idx+1)
            results_file = os.path.join(results_path,video_name,execution_metadata["processed_video_id"],chunk_name + '.pickle')
            create_pickle_file(results,results_file,logger = logger)
            chunk_metadata.update({"chunk": str(idx+1),"chunk_file": results_file})
            execution_metadata['chunks'].append(chunk_metadata)

        results_file = os.path.join(results_path,video_name,'processed_videos_metadata.json')
        add_dict_to_metadata_file(results_file, execution_metadata, logger = logger)

        process_end = time()
        process_time = str(process_end - process_start)
        logger.info(f'Total execution time = {process_time} seconds.')

    finally:
        if close_logger:
            log.shutdown_logger()