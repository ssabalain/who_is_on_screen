# import sys
# sys.path.append('/usr/local/python_scripts/')
import ops_check_packages as cp

packages_required = [
    "mysql-connector-python",
    "pandas",
    "sqlalchemy",
    "pymysql",
    "numpy"
    ]

for packs in packages_required:
  cp.install(packs)

import mysql.connector
import pandas as pd
from sqlalchemy import create_engine
import numpy as np
import time

def connect_to_mysql(db_user,pwd,database_name = None):
    if database_name == None:
        print("Connecting to MySQL (no database specified)")
        conn = mysql.connector.connect(user= db_user, password= pwd, host= 'mysql')
    else:
        print("Connecting to MySQL, database: " + database_name)
        conn = mysql.connector.connect(user= db_user, password= pwd, host= 'mysql', database= database_name)
    mycursor = conn.cursor()
    return conn,mycursor

def create_database(db_user,pwd,database_name):
    conn,sql_cursor = connect_to_mysql(db_user,pwd)
    existing_databases = show_databases(db_user,pwd)

    if database_name in existing_databases:
        print(f"Database '{database_name}' already exists.")
    else:
        print("Creating database '" + database_name + "'")
        query = "CREATE DATABASE " + database_name
        sql_cursor.execute(query)
        print(f'Database {database_name} created.')


def show_databases(db_user,pwd):
    conn,sql_cursor = connect_to_mysql(db_user,pwd)
    sql_cursor.execute("SHOW DATABASES")
    databases = []
    for x in sql_cursor:
        databases.append(x[0])

    return databases

def create_table(db_user,pwd,database_name,table_name,columns):
    conn,sql_cursor = connect_to_mysql(db_user,pwd,database_name)
    query_cols = " ("
    for column in columns:
        query_cols = query_cols + column['column_name'] +" " + column['sql_data_type'] + ", "
    query_cols = query_cols[:-2] + ")"
    
    query = "CREATE TABLE " + table_name + query_cols
    print("Creating table '" + table_name + "'")
    sql_cursor.execute(query)
    print("Table '" + table_name + "' created.")

def drop_table(db_user,pwd,database_name,table_name):
    conn,sql_cursor = connect_to_mysql(db_user,pwd,database_name)
    print("Dropping table " + table_name)
    sql_cursor.execute("DROP TABLE IF EXISTS "+table_name)

def return_conn(uri):
    conn = create_engine(uri, echo=False)
    return conn

def insert_df_in_table(conn,file_path,dtypes,chunk_size,table_name):
    batch_no = 0
    starttime = time.time()
    for chunk in pd.read_csv(file_path,compression='gzip', sep= '\t',dtype= dtypes,chunksize=chunk_size,iterator=True):
        chunk.to_sql(con = conn, name = table_name, if_exists = 'append',index= False)
        #Can be done using sqlAlchemy, but it's slower:
        #db.insert_df_in_table_2(conn,cursor,chunk,table_name)
        batch_no+=1

        if ((batch_no % 25) == 0 or batch_no == 1):
            print("Inserting records from batch: " + str(batch_no) + " of table " + table_name + ". Batch size: " + str(chunk_size))
    
    endtime = time.time()
    print("All records for table " + table_name + " were inserted. Overall execution time (secs): " + str(endtime - starttime))

def insert_pd_df_in_table(conn,df,table_name,if_exists_method='append'):
    starttime = time.time()
    df.to_sql(con = conn, name = table_name, if_exists = if_exists_method,index= False)
    endtime = time.time()
    print("All records for table " + table_name + " were inserted. Overall execution time (secs): " + str(endtime - starttime))

# Define function using cursor.executemany() to insert the dataframe
#This method has a little trouble around managing "Nan" values. In order to use it, the DF must NOT have any NaN values, otherwise it will
#throw an error. For that reason, we are using SQLAlchemy method (toSql). However, it's important to notice that the "ExecuteMany" method
#has proved to be a faster method than the SQL Alchemy one.
def insert_df_in_table_2(conn,cursor, df, table):
    
    # Creating a list of tupples from the dataframe values
    tpls = [tuple(x) for x in df.to_numpy()]
    
    # dataframe columns with Comma-separated
    cols = ','.join(list(df.columns))
    numcols = "%s," * len(df.columns) 
    sql_1 = "INSERT INTO %s(%s) VALUES(" % (table, cols)

    # SQL query to execute
    sql = sql_1 + numcols[:-1] + ")"
    cursor.executemany(sql, tpls)
    conn.commit()