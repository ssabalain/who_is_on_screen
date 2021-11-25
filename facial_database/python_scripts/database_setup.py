#%%
# import sys
# sys.path.append('/usr/local/python_scripts/')
import check_packages as cp

packages_required = ["mysql-connector-python","pandas"]

for packs in packages_required:
  cp.install(packs)
#%%
import mysql.connector
import pandas as pd


def connect_to_mysql(db_user,pwd):
    conn = mysql.connector.connect(user= db_user, password= pwd, host= 'mysql')
    # print("Connection status: " + str(conn.is_connected()))
    mycursor = conn.cursor()
    return conn,mycursor


def create_database(db_user,pwd,database_name):
    conn,sql_cursor = connect_to_mysql(db_user,pwd)
    #TO DO: check if database already exists... something with :mycursor.execute("SHOW DATABASES")
    #for x in mycursor:
    #print(x)
    query = "CREATE DATABASE " + database_name
    sql_cursor.execute(query)

def show_databases(db_user,pwd):
    conn,sql_cursor = connect_to_mysql(db_user,pwd)
    sql_cursor.execute("SHOW DATABASES")
    for x in sql_cursor:
        print(x)


columns = [['name','VARCHAR(255)'],
           ['age','int']]

def create_table(db_user,pwd,database_name,table_name,columns):
    sql_cursor = connect_to_mysql(db_user,pwd)
    query_cols = " ("
    for i in range(len(columns)):
        query_cols = query_cols + columns[i][0] +" " + columns[i][1] + ", "
    query_cols = query_cols[:-2] + ")"
    
    query = "CREATE TABLE " + database_name + query_cols
    sql_cursor.execute(query)



