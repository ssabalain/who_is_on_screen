import os
from ops_download_images import create_facial_dataset
from ops_logger import create_logger, shutdown_logger
from ops_face_detection import get_actors_embeddings
from setup_director_database import create_director_database

def download_facial_dataset():
    logger = create_logger(script_name = os.path.basename(__name__))
    sql_data = {'user':'WIOS_User','pwd':'Whoisonscreen!','database':'christopher_nolan'}
    movies = ['Inception']
    actors_per_movie = 12
    images_by_actor = 35
    dataset_folder = './datasets/actor_faces/'
    create_facial_dataset(movies,actors_per_movie,sql_data,dataset_folder, images_by_actor,logger = logger)
    shutdown_logger(logger)

def create_embeddings_model():
    logger = create_logger(script_name = os.path.basename(__name__), log_level = 'DEBUG')
    dataset_folder = './datasets/actor_faces/'
    models_folder = './models/embeddings/actor_faces'
    get_actors_embeddings(dataset_folder,save_to_pickle=True,output_folder=models_folder,logger = logger)
    shutdown_logger(logger)

def main():
    download_facial_dataset()
    create_embeddings_model()

# if __name__ == '__main__':
#     #This section shall be uncommented when the script is run from the command line.
#     #It should remain commented when the script is run from another python script or from Airflow.
#     main()