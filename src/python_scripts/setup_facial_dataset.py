import os
import ops_check_packages as cp
import ops_database_operations as db
import ops_download_images as di

packages_required = [
    "pandas"
    ]

for packs in packages_required:
  cp.install(packs)

import pandas as pd

def create_facial_dataset(movies, actors_per_movie, sql_dict, dataset_folder, images_by_actor):
    sql_user = sql_dict['user']
    sql_pwd = sql_dict['pwd']
    db_name = sql_dict['database']
    movies_string = "'" + "','".join(movies) + "'"
    query = f"""
        with base as (
            select
                m.original_title,
                a.actor_id,
                a.name,
                axm.character,
                axm.order as movie_order,
                row_number() over(partition by m.original_title order by axm.order) as limit_rank
            from actors_by_movie as axm
            join actors as a on axm.actor_id = a.actor_id
            join movies as m on axm.movie_id = m.movie_id
            where original_title in ({movies_string})
                and axm.character not like '%uncredited%'
                and axm.character not like '%(voice)%'
                and a.popularity > 3
        )
        
        select * from base where limit_rank <= {actors_per_movie} order by movie_order
        """
    actors_array = db.return_array_from_query(sql_user,sql_pwd,db_name,query)

    for actor in actors_array:
        actor_name = actor['name'].replace(' ','_').lower()
        actor_folder_name = str(actor['actor_id']) + '_' + actor_name
        actor_full_path = os.path.join(dataset_folder,actor_folder_name)
        actor_search_query = actor['name'] + ' face'
        actor_movie_name = actor_name + "_" + actor['original_title'].replace(' ','_').lower()
        actor_movie_search_query = actor['name'] + ' face ' + actor['original_title']

        if not os.path.isdir(actor_full_path):
            di.get_images_on_folder(actor_full_path, actor_search_query,actor_name, images_by_actor)
            di.get_images_on_folder(actor_full_path, actor_movie_search_query, actor_movie_name, 3)

        else:
            di.get_images_on_folder(actor_full_path, actor_movie_search_query, actor_movie_name, 3)

def main():
    sql_data = {'user':'WIOS_User','pwd':'Whoisonscreen!','database':'christopher_nolan'}
    movies = ['Inception']
    actors_per_movie = 15
    images_by_actor = 10
    dataset_folder = '/opt/workspace/src/datasets/actor_faces/'
    create_facial_dataset(movies,actors_per_movie,sql_data,dataset_folder, images_by_actor)