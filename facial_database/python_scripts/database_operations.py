# import sys
# sys.path.append('/usr/local/python_scripts/')
import check_packages as cp

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

def connect_to_mysql(db_user,pwd,database_name = None):
    if database_name == None:
        print("Connecting to MySQL (no database specified)")
        conn = mysql.connector.connect(user= db_user, password= pwd, host= 'mysql')
    else:
        print("Connecting to MySQL,database: " + database_name)
        conn = mysql.connector.connect(user= db_user, password= pwd, host= 'mysql', database= database_name)
    # print("Connection status: " + str(conn.is_connected()))
    mycursor = conn.cursor()
    return conn,mycursor

#This one doesnt work :( there are some user access problems... workaround: create database directly on docker-compose
def create_database(db_user,pwd,database_name):
    conn,sql_cursor = connect_to_mysql(db_user,pwd)
    query = "CREATE DATABASE " + database_name
    sql_cursor.execute(query)

def show_databases(db_user,pwd):
    conn,sql_cursor = connect_to_mysql(db_user,pwd)
    sql_cursor.execute("SHOW DATABASES")
    for x in sql_cursor:
        print(x)

def create_table(db_user,pwd,database_name,table_name,columns):
    conn,sql_cursor = connect_to_mysql(db_user,pwd,database_name)
    query_cols = " ("
    for i in range(len(columns)):
        query_cols = query_cols + columns[i][0] +" " + columns[i][1] + ", "
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

# Define function using cursor.executemany() to insert the dataframe
#This methos has a little trouble around managing "Nan" values. In order to use it, the DF must NOT have any NaN values, otherwise it will
#throw an error. For that reason, we are using SQLAlchemy method (toSql). However, it's important to notice that the "ExecuteMany" method
#has proved to be a faster method than the SQL Alchemy one.
def insert_df_in_table(conn,cursor, df, table):
    
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


