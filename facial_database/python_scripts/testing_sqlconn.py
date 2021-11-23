import sys
sys.path.append('/usr/local/python_scripts/')
import check_packages as cp

packages_required = ["mysql-connector-python","pandas"]

for packs in packages_required:
  cp.install(packs)

import mysql.connector
import pandas as pd

def create_table(mycursor):
  mycursor.execute("CREATE TABLE testingtable (name VARCHAR(200), age INT)")

def insert_records(conn,mycursor):
  sql = "INSERT INTO testingtable (name,age) VALUES (%s, %s)"
  val = [("Santi",26),("Rocio",26)]

  mycursor.executemany(sql,val)
  conn.commit()

def show_records(mycursor):
  mycursor.execute("SELECT * FROM testingtable")
  myresult = mycursor.fetchall()
  for x in myresult:
    print(x)

def main(option):
  conn = mysql.connector.connect(user='ssabalain', password='Whoisonscreen!', host='mysql', database='test_database')
  print("Connection status: " + str(conn.is_connected()))
  mycursor = conn.cursor()
  # option = sys.argv[1]

  if option == '1':
    create_table(mycursor)
  elif option == '2':
    insert_records(conn,mycursor)
  elif option == '3':
    show_records(mycursor)
  else:
    print("Please enter a valid option")
  conn.close()

def mainagain():
  main('3')

mainagain()