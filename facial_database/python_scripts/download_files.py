import check_packages as cp

packages_required = ["pandas","requests"]

for packs in packages_required:
  cp.install(packs)

import pandas as pd
import requests
import os
import gc

def download_file_from_url(url,folder_path):
    #Downloading the file into datasets folder
    filename = url.split("/")[-1]
    with open(folder_path+filename, "wb") as f:
        r = requests.get(url)
        f.write(r.content)
    print("File " + filename + " succesfully downloaded.")

def download_datasets(folder_path,url):
    #Creating datasets folder in case it doesnt exists
    if os.path.exists(folder_path) == False:
        print("Path folder didn't exists, we'll create it")  
        os.makedirs(folder_path)

    filename = url.split("/")[-1]
    if os.path.isfile(folder_path + filename) == False:
        print("Downloading file " + filename)
        download_file_from_url(url,folder_path)
    else:
        print("File " + filename + " already in filesystem.")

# def return_movies_by_director(director_name,birth_year,people,titles,crew_by_title):
#     #Filtering & mergind datasets to get the list of movies from given director
#     director_id = people[(people['primaryName'] == director_name) & (people['birthYear'] == birth_year)]['nconst'].iat[0]
#     print("Filtering movies by given director")
#     director_movies = pd.merge(titles,
#                         crew_by_title[crew_by_title['directors'] == director_id]['tconst'],
#                         how = 'inner', 
#                         on ='tconst') 
#     return(director_movies[director_movies['titleType'] == 'movie'])

# def return_actors(director,director_birthYear,movies_from,movies_to,datasets_folder):
#     os.chdir("..")
#     #We download any dataset if needed
#     download_datasets(datasets_folder)

#     #Reading CSV files and putting them into a DF
#     print("Reading peoples DF")
#     people_dtypes = {'nconst': str,'primaryName':str,'birthYear':str,'deathYear':str,'primaryProfession ':object, 'knownForTitles': object}
#     people_df = pd.read_csv('./imbd_datasets/name.basics.tsv.gz',compression='gzip', sep= '\t',dtype= people_dtypes)
#     print("Reading titles DF")
#     titles_dtypes = {'tconst': str,'titleType':str,'primaryTitle':str,'originalTitle':str,'isAdult':str,'startYear':str,'endYear': str,'runtimeMinutes':str,'genres':object}
#     titles_df = pd.read_csv('./imbd_datasets/title.basics.tsv.gz',compression='gzip', sep= '\t',dtype= titles_dtypes)
#     print("Reading crew by title DF")
#     crew_by_title_dtypes = {'tconst':str,'directors':object,'writers':object}
#     crew_by_title_df = pd.read_csv('./imbd_datasets/title.crew.tsv.gz',compression='gzip', sep= '\t',dtype= crew_by_title_dtypes)
   
#     director_movies_raw = return_movies_by_director(director,director_birthYear,people_df,titles_df,crew_by_title_df)
#     director_movies =  director_movies_raw[ (director_movies_raw['startYear'] > movies_from) & 
#                                             (director_movies_raw['startYear'] < movies_to)
#                                             ]
    
#     del titles_df,crew_by_title_df, director_movies_raw
#     gc.collect()

#     print("Reading actors by title DF")
#     actor_by_title_dtypes = {'tconst': str, 'ordering':int,'nconst':str,'category':str,'job':str,'characters':str}
#     actor_by_title_df = pd.read_csv('./imbd_datasets/title.principals.tsv.gz',compression='gzip', sep= '\t',dtype= actor_by_title_dtypes)

#     print("Gathering all actors by movie")
#     people_by_movies = pd.merge(
#                             pd.merge(actor_by_title_df,
#                                     director_movies,
#                                     how= 'inner',
#                                     on = 'tconst'
#                                     ),
#                             people_df,
#                             how= 'inner',
#                             on = 'nconst'
#                             )

#     del people_df, actor_by_title_df, director_movies
#     gc.collect()

#     actor_by_movies = people_by_movies[(people_by_movies['category'] == 'actor') |(people_by_movies['category'] == 'actress') ][['tconst','nconst','primaryTitle','originalTitle','primaryName','characters']]
#     return(actor_by_movies)

# def return_df(df_name,datasets_folder):
    # os.chdir("..")
    # download_datasets(datasets_folder) 

    # if df_name == 'peoples':
    #     print("Reading peoples DF")
    #     people_dtypes = {'nconst': str,'primaryName':str,'birthYear':str,'deathYear':str,'primaryProfession ':object, 'knownForTitles': object}
    #     people_df = pd.read_csv('./imbd_datasets/name.basics.tsv.gz',compression='gzip', sep= '\t',dtype= people_dtypes)
    #     print("Dataset already read, returning dataframe")
    #     return people_df
    # elif df_name == 'titles':
    #     print("Reading titles DF")
    #     titles_dtypes = {'tconst': str,'titleType':str,'primaryTitle':str,'originalTitle':str,'isAdult':str,'startYear':str,'endYear': str,'runtimeMinutes':str,'genres':object}
    #     titles_df = pd.read_csv('./imbd_datasets/title.basics.tsv.gz',compression='gzip', sep= '\t',dtype= titles_dtypes)
    #     print("Dataset already read, returning dataframe")
    #     return titles_df
    # elif df_name == 'crew_by_title':
    #     print("Reading crew by title DF")
    #     crew_by_title_dtypes = {'tconst':str,'directors':object,'writers':object}
    #     crew_by_title_df = pd.read_csv('./imbd_datasets/title.crew.tsv.gz',compression='gzip', sep= '\t',dtype= crew_by_title_dtypes)
    #     print("Dataset already read, returning dataframe")
    #     return crew_by_title_df
    # elif df_name == 'actors_by_title':
    #     print("Reading actors by title DF")
    #     actor_by_title_dtypes = {'tconst': str, 'ordering':int,'nconst':str,'category':str,'job':str,'characters':str}
    #     actor_by_title_df = pd.read_csv('./imbd_datasets/title.principals.tsv.gz',compression='gzip', sep= '\t',dtype= actor_by_title_dtypes)
    #     print("Dataset already read, returning dataframe")
    #     return actor_by_title_df
    # else:
    #     print("You haven't choose a correct DF, please try again")


# Director= 'Christopher Nolan'
# Director_birthyear = '1970'
# Movies_from = '2004'
# Movies_to = '2021'

# # actors_df = ea.return_actors(  director=Director,
# #                             director_birthYear= Director_birthyear,
# #                             movies_from= Movies_from,
# #                             movies_to= Movies_to,
# #                             datasets_folder= Datasets_folder
# #                             )

# # print(actors_df)
