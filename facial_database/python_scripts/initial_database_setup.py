def main():
    import check_packages as cp

    packages_required = [
        "pandas"
        ]

    for packs in packages_required:
        cp.check_package(packs)

    import os
    root_facialdb_folder = "/usr/local/facial_database/"
    os.chdir(root_facialdb_folder)

    import time
    import pandas as pd
    import database_operations as db
    import download_files as df

    datasets_folder = 'imdb_datasets/'    
    sql_user = 'WIOS_User'
    sql_pwd = 'Whoisonscreen!'
    db_name = 'facial_db'
    uri = 'mysql+pymysql://' + sql_user + ':' + sql_pwd + '@' + 'mysql' + ':' + '3306' + '/' + db_name #sqlAlchemyVersion

    #Metadata from the IMBD datasets. Can be accesed here: https://www.imdb.com/interfaces/
    imbd_datasets = [
        [
            ['imdb_crew_by_title'],                                 #Table Name
            [                                                       #Table Columns
                ['tconst','VARCHAR(15)'],
                ['directors','TEXT'],
                ['writers','TEXT']
            ],
            ['title.crew.tsv.gz'],                                  #File name
            [{'tconst':str,'directors':object,'writers':object}]    #Table datatypes (in order to make pandas reading faster)
        ],
        [
            ['imdb_peoples'],
            [
                ['nconst','VARCHAR(15)'],
                ['primaryName','TEXT'],
                ['birthYear','VARCHAR(5)'],
                ['deathYear','VARCHAR(5)'],
                ['primaryProfession','TEXT'],
                ['knownForTitles','TEXT']
            ],
            ['name.basics.tsv.gz'],
            [{'nconst': str,'primaryName':str,'birthYear':str,'deathYear':str,'primaryProfession ':object, 'knownForTitles': object}]
        ],
        [
            ['imdb_titles'],
            [
                ['tconst','VARCHAR(15)'],
                ['titleType','VARCHAR(25)'],
                ['primaryTitle','TEXT'],
                ['originalTitle','TEXT'],
                ['isAdult','VARCHAR(5)'],
                ['startYear','VARCHAR(5)'],
                ['endYear','VARCHAR(5)'],
                ['runtimeMinutes','VARCHAR(100)'],
                ['genres','TEXT'],
            ],
            ['title.basics.tsv.gz'],
            [{'tconst': str,'titleType':str,'primaryTitle':str,'originalTitle':str,'isAdult':str,'startYear':str,'endYear': str,'runtimeMinutes':str,'genres':object}]
        ],
        [
            ['imdb_actors_by_title'],
            [
                ['tconst','VARCHAR(15)'],
                ['ordering','INT'],
                ['nconst','VARCHAR(15)'],
                ['category','VARCHAR(25)'],
                ['job','TEXT'],
                ['characters','TEXT']
            ],
            ['title.principals.tsv.gz'],
            [{'tconst': str, 'ordering':int,'nconst':str,'category':str,'job':str,'characters':str}]
        ]
    ]

    conn = db.return_conn(uri) #sqlAlchemy version
    #conn,cursor = db.connect_to_mysql(sql_user,sql_pwd,db_name)
    dropping = 1
    
    for j in range(0,len(imbd_datasets)):
        file_to_download = imbd_datasets[j][2][0]
        #Downloading the IMDB files if needed
        df.download_datasets(root_facialdb_folder + datasets_folder,"https://datasets.imdbws.com/"+ file_to_download)

    #Creating tables in SQL and loading the data from the .tsv files
    for i in range(0,len(imbd_datasets)):
        table_name = imbd_datasets[i][0][0]
        columns = imbd_datasets[i][1]
        file_name = imbd_datasets[i][2][0]
        dtypes = imbd_datasets[i][3][0]

        #Creating the tables. If dropping is enables, we will first drop the existing tables
        if dropping == 1:
            db.drop_table(sql_user,sql_pwd,db_name,table_name)

        db.create_table(sql_user,sql_pwd,db_name,table_name,columns)
        
        #Loading the data all at once is not possible due to RAM overloading. In order to acoomplish the upload, we'll perform a chuck load.
        #Chunk size can be modified according to available resources.
        chunk_size=100000
        batch_no=0

        file_path = root_facialdb_folder + datasets_folder + file_name

        starttime = time.time()
        for chunk in pd.read_csv(file_path,compression='gzip', sep= '\t',dtype= dtypes,chunksize=chunk_size,iterator=True):
            chunk.to_sql(con = conn, name = table_name, if_exists = 'append',index= False) #Can be done using sqlAlchemy, but it's slower
            #db.insert_df_in_table(conn,cursor,chunk,table_name)
            batch_no+=1

            if ((batch_no % 25) == 0 or batch_no == 1):
                print("Inserting records from batch: " + str(batch_no) + " of table " + table_name + ". Batch size: " + str(chunk_size))
        
        endtime = time.time()
        print("All records for table " + table_name + " were inserted. Overall execution time (secs): " + str(endtime - starttime))

# if __name__ == '__main__':
#     main()