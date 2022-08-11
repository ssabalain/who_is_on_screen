from imutils import paths
import numpy as np
import imutils
import cv2
import os
import matplotlib.pyplot as plt
from time import time
from datetime import datetime
import imghdr
import ops_logger as log
import ops_files_operations as files

#Set 'src' folder as the working directory
script_name = os.path.basename(__name__)
path_arr = os.getcwd().split(os.path.sep)
os.chdir(os.path.sep.join(path_arr[:path_arr.index('src')+1]))

def path_index(image_path):
    return int(image_path.split(os.path.sep)[-1].split('.')[0].split('_')[-1])

def get_actors_dict(actor_faces_folder):
    image_paths = list(paths.list_images(actor_faces_folder))
    actors_dict = {}

    for (i, image_path) in enumerate(image_paths):
        actor_name = image_path.split(os.path.sep)[3]

        if actor_name not in actors_dict.keys():
            actors_dict[actor_name] = []

        actors_dict[actor_name].append(image_path)

    for actor, actors_images in actors_dict.items():
        actors_images.sort(key = path_index)

    return(actors_dict)

def get_embeddings_from_image(img_path, opencv_dnn_model,embedder,logger,multiple_faces = False, min_confidence=0.9, display=False):

    logger.debug(f'Starting face detection. Multiple faces: {multiple_faces}. Minimun confidence: {min_confidence}. Display mode: {display}')
    scanned_faces = 0
    embeddings = []
    admited_file_types = ['jpeg','png','webp',None]
    file_format = imghdr.what(img_path)

    if file_format not in admited_file_types:
        raise ValueError('The image provided is not withing the admited file formats',file_format)

    image = cv2.imread(img_path)
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

    for face in results[0][0]:
        if not multiple_faces:
            if iteration != i:
                continue

        iteration+=1
        face_confidence = face[2]

        if face_confidence > min_confidence:

            logger.debug(f'Scanning face {iteration}. Face confidence: {face_confidence}.')

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

    else:
        return embeddings

def get_actors_embeddings(actor_faces_folder,logger,images_per_actor = None):
    process_start = time()
    actors_dict = get_actors_dict(actor_faces_folder)
    logger.info(f'Totals actors retrieved: {len(actors_dict)}.')

    protoPath = './models/face_detector/deploy.prototxt'
    modelPath = './models/face_detector/res10_300x300_ssd_iter_140000.caffemodel'
    embeddingPath = './models/face_detector/openface.nn4.small2.v1.t7'
    detector = cv2.dnn.readNetFromCaffe(protoPath, modelPath)
    embedder = cv2.dnn.readNetFromTorch(embeddingPath)

    actors_names = []
    actors_embeddings = []

    for actor, actors_images in actors_dict.items():
        processed_images = 0
        if images_per_actor is None:
            images_per_actor = len(actors_images)

        logger.info(f'Analyzing actor {actor}. Total images available: {len(actors_images)}. Images to process: {images_per_actor}')

        for (i, img_path) in enumerate(actors_images):
            if i + 1 > images_per_actor:
                continue

            logger.debug(f'Getting embeddings for image {i+1}/{images_per_actor} for actor {actor}.')
            try:
                img_embeddings = get_embeddings_from_image(img_path,detector,embedder,logger)
            except ValueError as err:
                logger.error(err)
                continue
            
            if len(img_embeddings) == 1:
                if len(img_embeddings[0]) == 128:
                    processed_images+=1
                    actors_names.append(actor)
                    actors_embeddings.append(img_embeddings)
            else:
                logger.debug("Embedding is not 128, so we skip it.")
                continue

        logger.info(f'{processed_images}/{images_per_actor} images for actor {actor} were processed.')
        images_per_actor = None

    emb_dict = {"embeddings": actors_embeddings, "names": actors_names}
    process_end = time()
    process_time = str(process_end - process_start)
    logger.info(f'Embedding extraction finished. Exec time: {process_time}.')
    return emb_dict

def main():
    log_folder = './models/logs'
    faces_dataset_folder = './datasets/actor_faces'
    embeddings_file = './models/embeddings/embeddings.pickle'

    logger = log.create_logger(log_folder,script_name,level='info')
    embeddings = get_actors_embeddings(faces_dataset_folder,logger)
    files.create_pickle_file(embeddings,embeddings_file,logger)
    log.shutdown_logger(logger)

if __name__ == '__main__':
    main()