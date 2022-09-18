import os
from ops_download_images import create_facial_dataset
from ops_logger import Logger
from ops_face_detection import get_actors_embeddings
from setup_director_database import create_director_database

def download_facial_dataset():
    log = Logger(script_name = os.path.basename(__name__))
    log.create_logger()
    logger = log.logger
    sql_data = {'user':'WIOS_User','pwd':'Whoisonscreen!','database':'christopher_nolan'}
    movies = ['Inception']
    actors_per_movie = 12
    images_by_actor = 35
    dataset_folder = './datasets/actor_faces/'
    create_facial_dataset(movies,actors_per_movie,sql_data,dataset_folder, images_by_actor,logger = logger)
    log.shutdown_logger()

def create_embeddings_model():
    log = Logger(script_name = os.path.basename(__name__))
    log.create_logger()
    logger = log.logger
    dataset_folder = './datasets/actor_faces/'
    models_folder = './models/embeddings/actor_faces'
    get_actors_embeddings(dataset_folder,save_to_pickle=True,output_folder=models_folder,logger = logger)
    log.shutdown_logger()

def main():
    download_facial_dataset()
    create_embeddings_model()

# if __name__ == '__main__':
#     #This section shall be uncommented when the script is run from the command line.
#     #It should remain commented when the script is run from another python script or from Airflow.
#     main()