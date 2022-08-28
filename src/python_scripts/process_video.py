import os
from ops_logger import create_logger, shutdown_logger
from ops_face_detection import get_video_embeddings

def get_scene_embeddings():
    logger = create_logger(script_name = os.path.basename(__name__))
    video_path = './datasets/videos/the_final_kick.mp4'
    results_path = './models/embeddings/processed_videos'
    get_video_embeddings(video_path,results_path,partitions = 4,desired_fps = 1,logger = logger)
    shutdown_logger(logger)

def main():
    get_scene_embeddings()

# if __name__ == '__main__':
#     #This section shall be uncommented when the script is run from the command line.
#     #It should remain commented when the script is run from another python script or from Airflow.
#     main()