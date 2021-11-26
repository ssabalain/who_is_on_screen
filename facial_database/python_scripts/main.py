def main():
    import extract_actors as ea

    Director= 'Christopher Nolan'
    Director_birthyear = '1970'
    Movies_from = '2004'
    Movies_to = '2021'
    Datasets_folder = './imbd_datasets/'

    actors_df = ea.return_actors(  director=Director,
                                director_birthYear= Director_birthyear,
                                movies_from= Movies_from,
                                movies_to= Movies_to,
                                datasets_folder= Datasets_folder
                                )

    print(actors_df)

    import database_setup as db
    sql_user = 'WIOS_User'
    sql_pwd = 'Whoisonscreen!'
    db_name = 'facial_db'
    table_name = 'testing'
    table_columns = [
        ['name','VARCHAR(255)'],
        ['age','int']
    ]

    db.show_databases(sql_user,sql_pwd)    
    db.create_table(sql_user,sql_pwd,db_name,table_name,table_columns)


if __name__ == '__main__':
    main()