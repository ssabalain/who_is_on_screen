import check_packages as cp
import os
root_facialdb_folder = "/usr/local/facial_database/"
os.chdir(root_facialdb_folder)

import pandas as pd
import json
import time
import database_operations as db
import download_files as df

datasets_folder = 'datasets/imdb_datasets/'
#Metadata from the IMDB datasets. Can be accessed here: https://www.imdb.com/interfaces/
imdb_metadata_folder = 'python_scripts/'
imdb_metadata_file = 'imdb_metadata.json'

#MySQL metadata (defined in docker-compose file)
sql_user = 'WIOS_User'
sql_pwd = 'Whoisonscreen!'
db_name = 'facial_db'
uri = 'mysql+pymysql://' + sql_user + ':' + sql_pwd + '@' + 'mysql' + ':' + '3306' + '/' + db_name #sqlAlchemyVersion
dropping = 1 #1 if we want to drop the tables before generating them

def download_datasets():

    imdb_datasets = json.load(open(root_facialdb_folder + imdb_metadata_folder + imdb_metadata_file))
    packages_required = ["pandas"]

    for packs in packages_required:
        cp.check_package(packs)

    for datasets in imdb_datasets['datasets']:
        file_to_download = datasets['file_name']
        #Downloading the IMDB files if needed
        df.download_datasets(root_facialdb_folder + datasets_folder,"https://datasets.imdbws.com/"+ file_to_download)

def drop_all_tables():

    imdb_datasets = json.load(open(root_facialdb_folder + imdb_metadata_folder + imdb_metadata_file))

    for datasets in imdb_datasets['datasets']:
        db.drop_table(sql_user,sql_pwd,db_name,datasets['name'])

def main():

    conn = db.return_conn(uri) #sqlAlchemy version
    #conn,cursor = db.connect_to_mysql(sql_user,sql_pwd,db_name)

    download_datasets()

    #If dropping is enabled, we will first drop the existing tables
    if dropping == 1:
        drop_all_tables()

    imdb_datasets = json.load(open(root_facialdb_folder + imdb_metadata_folder + imdb_metadata_file))

    #Creating tables in SQL and loading the data from the .tsv files
    for datasets in imdb_datasets['datasets']:
        table_name = datasets['name']
        columns = datasets['columns']
        file_name = datasets['file_name']
        dtypes = {}

        for columns in datasets['columns']:
            key = columns['column_name']
            dtypes[key] = columns['py_data_type']

        columns = datasets['columns']
        db.create_table(sql_user,sql_pwd,db_name,table_name,columns)
        
        #Loading the data all at once is not possible due to RAM overloading. In order to accomplish the upload,
        #   we'll perform a chunck load.
        #Chunk size can be modified according to available resources.
        chunk_size=100000
        batch_no=0

        file_path = root_facialdb_folder + datasets_folder + file_name

        starttime = time.time()
        for chunk in pd.read_csv(file_path,compression='gzip', sep= '\t',dtype= dtypes,chunksize=chunk_size,iterator=True):
            chunk.to_sql(con = conn, name = table_name, if_exists = 'append',index= False) 
            #Can be done using sqlAlchemy, but it's slower:
            #db.insert_df_in_table(conn,cursor,chunk,table_name)
            batch_no+=1

            if ((batch_no % 25) == 0 or batch_no == 1):
                print("Inserting records from batch: " + str(batch_no) + " of table " + table_name + ". Batch size: " + str(chunk_size))
        
        endtime = time.time()
        print("All records for table " + table_name + " were inserted. Overall execution time (secs): " + str(endtime - starttime))

# if __name__ == '__main__':
#     main()