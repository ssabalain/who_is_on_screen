#%%
import pandas as pd
import requests
import os

def download_file_from_url(url,folder_path):
    #Downloading the file into datasets folder
    filename = url.split("/")[-1]
    with open(folder_path+filename, "wb") as f:
        r = requests.get(url)
        f.write(r.content)

def download_datasets(folder_path):
    url_list = [
    "https://datasets.imdbws.com/title.basics.tsv.gz",
    "https://datasets.imdbws.com/name.basics.tsv.gz",
    "https://datasets.imdbws.com/title.crew.tsv.gz",
    "https://datasets.imdbws.com/title.principals.tsv.gz"
    ]

    #Creating datasets folder in case it doesnt exists
    if not os.path.exists(folder_path):
        print("Path folder didn't exists, we'll create it")  
        os.makedirs(folder_path)

    for url in url_list:
        filename = url.split("/")[-1]
        if not os.path.isfile(folder_path + filename):
            print("Downloading file " + filename)
            download_file_from_url(url,datasets_folder)

def return_movies_by_director(director_name,birth_year,people,titles,crew_by_title):
    #Filtering & mergind datasets to get the list of movies from given director
    director_id = people[(people['primaryName'] == director_name) & (people['birthYear'] == birth_year)]['nconst'].iat[0]
    print("Filtering movies by given director")
    director_movies = pd.merge(titles,
                        crew_by_title[crew_by_title['directors'] == director_id]['tconst'],
                        how = 'inner', 
                        on ='tconst') 
    return(director_movies[director_movies['titleType'] == 'movie'])

def return_actors(director,director_birthYear,movies_from,movies_to,datasets_folder):
    #We download any dataset if needed
    download_datasets(datasets_folder)

    #Reading CSV files and putting them into a DF
    print("Reading peoples DF")
    people_df = pd.read_csv('./imbd_datasets/name.basics.tsv.gz',compression='gzip', sep= '\t',low_memory= False)
    print("Reading titles DF")
    titles_df = pd.read_csv('./imbd_datasets/title.basics.tsv.gz',compression='gzip', sep= '\t',low_memory= False)
    print("Reading crew by title DF")
    crew_by_title_df = pd.read_csv('./imbd_datasets/title.crew.tsv.gz',compression='gzip', sep= '\t',low_memory= False)
    print("Reading actors by title DF")
    actor_by_title_df = pd.read_csv('./imbd_datasets/title.principals.tsv.gz',compression='gzip', sep= '\t',low_memory= False)

    director_movies_raw = return_movies_by_director(director,director_birthYear,people_df,titles_df,crew_by_title_df)
    director_movies =  director_movies_raw[ (director_movies_raw['startYear'] > movies_from) & 
                                            (director_movies_raw['startYear'] < movies_to)
                                            ]
    
    print("Gathering all actors by movie")
    people_by_movies = pd.merge(
                            pd.merge(actor_by_title_df,
                                    director_movies,
                                    how= 'inner',
                                    on = 'tconst'
                                    ),
                            people_df,
                            how= 'inner',
                            on = 'nconst'
                            )


    actor_by_movies = people_by_movies[(people_by_movies['category'] == 'actor') |(people_by_movies['category'] == 'actress') ][['tconst','nconst','primaryTitle','originalTitle','primaryName','characters']]
    return(actor_by_movies)

#%%
def main():
    Director= 'Christopher Nolan'
    Director_birthyear = '1970'
    Movies_from = '2004'
    Movies_to = '2021'
    Datasets_folder = './imbd_datasets/'

    actors_df = return_actors(  director=Director,
                                director_birthYear= Director_birthyear,
                                movies_from= Movies_from,
                                movies_to= Movies_to,
                                datasets_folder= Datasets_folder
                                )

    actors_df

if __name__ == '__main__':
    main()