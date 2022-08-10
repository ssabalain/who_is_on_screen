import json
import requests
import ops_check_packages as cp
import ops_database_operations as db

packages_required = [
    "pyyaml",
    "pandas"
    ]

for packs in packages_required:
  cp.install(packs)

import yaml
from yaml.loader import SafeLoader
import pandas as pd

def get_tmdb_id_for_person(person_name,api_key):
    searchable_name = '+'.join(person_name.split(' '))
    query = 'https://api.themoviedb.org/3/search/person?api_key='+ api_key +'&language=en-US&page=1&include_adult=false&query=' + searchable_name
    response = requests.get(query)
    if response.status_code==200:
        array = response.json()
        tmdb_id = array['results'][0]['id']
        return (tmdb_id)
    else:
        return ("error")

def get_movies_by_director(director_id,api_key):
    query = 'https://api.themoviedb.org/3/person/'+ str(director_id) +'/movie_credits?api_key='+ api_key +'&language=en-US'
    response = requests.get(query)
    if response.status_code==200:
        array = response.json()
        movies = [x for x in array['crew'] if x['job'] == 'Director']
        return (movies)
    else:
        return ("error")

def get_actors_by_movie(movie_id,api_key):
    query = 'https://api.themoviedb.org/3/movie/'+ str(movie_id) +'/credits?api_key='+ api_key +'&language=en-US'
    response = requests.get(query)
    if response.status_code==200:
        array = response.json()
        actors = array['cast']
        return (actors)
    else:
        return ("error")

def get_actor_by_id(actor_id, api_key):
    query = 'https://api.themoviedb.org/3/person/'+ str(actor_id) +'?api_key='+ api_key +'&language=en-US'
    response = requests.get(query)
    if response.status_code==200:
        array = response.json()
        return (array)
    else:
        return ("error")

def create_director_database(director_name,tmdb_keys_path,sql_user,sql_pwd):
    db_name = director_name.replace(' ','_').lower()

    with open(tmdb_keys_path) as f:
        tmdb_key = yaml.load(f, Loader=SafeLoader)['TMDB_API_KEY']

    director_tmdb_id = get_tmdb_id_for_person(director_name,tmdb_key)
    movies_from_director_array = get_movies_by_director(director_tmdb_id,tmdb_key)
    movies_from_director_df = pd.DataFrame.from_records(movies_from_director_array)[['id','original_title','release_date','vote_average','vote_count']]
    movies_from_director_df.rename(columns = {'id':'movie_id'}, inplace = True)

    db.create_database(sql_user,sql_pwd,db_name)

    uri = 'mysql+pymysql://' + sql_user + ':' + sql_pwd + '@' + 'mysql' + ':' + '3306' + '/' + db_name
    conn = db.return_conn(uri)
    db.insert_pd_df_in_table(conn,movies_from_director_df,'movies',if_exists_method = 'replace')

    actors_from_director_array = []

    actors_list = []
    actors_array = []

    for movie in movies_from_director_array:
        actors_from_movie_array = get_actors_by_movie(movie['id'],tmdb_key)
        for actor in actors_from_movie_array:
            if actor['id'] not in actors_list:
                actors_list.append(actor['id'])
                actors_array.append(actor)

            actor['movie_id'] = str(movie['id'])
            actors_from_director_array.append(actor)

    actors_from_director_df = pd.DataFrame.from_records(actors_from_director_array)[['id','movie_id','cast_id','credit_id','character','order']]
    actors_from_director_df.rename(columns = {'id':'actor_id'}, inplace = True)
    db.insert_pd_df_in_table(conn,actors_from_director_df,'actors_by_movie',if_exists_method = 'replace')

    actors_df = pd.DataFrame.from_records(actors_array)[['id','name','original_name','gender','popularity','known_for_department']]
    actors_df.rename(columns = {'id':'actor_id'}, inplace = True)
    db.insert_pd_df_in_table(conn,actors_df,'actors',if_exists_method = 'replace')

def main():
    director_name = 'Christopher Nolan'
    tmdb_keys_path = '/opt/workspace/src/keys.yml'
    sql_user = 'WIOS_User'
    sql_pwd = 'Whoisonscreen!'
    create_director_database(director_name,tmdb_keys_path,sql_user,sql_pwd)