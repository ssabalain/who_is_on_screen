import os
from ops_logger import Logger
from ops_face_detection import get_video_embeddings

def get_scene_embeddings():
    log = Logger(script_name = os.path.basename(__name__))
    log.create_logger()
    logger = log.logger
    video_path = './datasets/videos/the_final_kick.mp4'
    results_path = './models/embeddings/processed_videos'
    get_video_embeddings(video_path,results_path,partitions = 4,desired_fps = 1,logger = logger)
    log.shutdown_logger()

def main():
    get_scene_embeddings()

# if __name__ == '__main__':
#     #This section shall be uncommented when the script is run from the command line.
#     #It should remain commented when the script is run from another python script or from Airflow.
#     main()