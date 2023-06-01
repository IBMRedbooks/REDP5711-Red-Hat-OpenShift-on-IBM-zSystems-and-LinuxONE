#!/usr/bin/env python3

from redis import Redis
import os
import time
import psycopg2
import json

def get_redis():
   redishost = os.environ.get('REDIS_HOST', 'new-redis')
   redispassword = os.environ.get('REDIS_PASSWORD', 'password')
   print ("Connecting to Redis using " + redishost)
   #redis_conn = Redis(host=redishost, db=0, socket_timeout=5)
   redis_conn = Redis(host=redishost, db=0, socket_timeout=5, password=redispassword)
   redis_conn.ping()
   print ("connected to redis!") 
   return redis_conn

def connect_postgres(): 
   host = os.getenv('POSTGRES_SERVICE_HOST', "new-postgresql")
   db_name = os.getenv('DB_NAME', "db") 
   db_user = os.getenv('DB_USER', "admin") 
   db_pass = os.getenv('DB_PASS', "admin") 
   try:
      print ("connecting to the DB") 
      conn = psycopg2.connect ("host={} dbname={} user={} password={}".format(host, db_name, db_user, db_pass))
      print ("Successfully connected to Postgres")
      
      return conn 

   except Exception as e:
      print ("error connecting to the DB")
      print (e)

def create_postgres_table():
    try: 
       conn = connect_postgres()

    except Exception as e:
       print ("error connecting to postgres")  
       print (str(e)) 

    try:
       cursor = conn.cursor()
       sqlCreateTable = "CREATE TABLE IF NOT EXISTS public.votes (id VARCHAR(255) NOT NULL, vote VARCHAR(255) NOT NULL);"
       cursor.execute(sqlCreateTable)
       print ("votes table created") 
       conn.commit()
       cursor.close() 

    except Exception as e:
       print ("error creating database table")
       print (e)

    try:
      conn.close()

    except Exception as e:
       print ("error closing connection to postgres")
       print (str(e))


def insert_postgres(data):
    try:
       conn = connect_postgres()

    except Exception as e:
       print ("error connecting to postgres")  
       print (str(e)) 


    try:
       cur = conn.cursor()
       cur.execute("insert into votes values (%s, %s)",
       (
          data.get("voter_id"),
          data.get("vote")
       ))
       conn.commit()
       print ("row inserted into DB")
       cur.close()

    except Exception as e:
       conn.rollback()
       cur.close()
       print ("error inserting into postgres")
       print (str(e))

    try:
      conn.close()

    except Exception as e:
       print ("error closing connection to postgres")
       print (str(e))

def process_votes():
    redis = get_redis()
    redis.ping()  
    while True: 
       try:  
          msg = redis.rpop("votes")
          print(msg)
          if (msg != None): 
             print ("reading message from redis")
             msg_dict = json.loads(msg)
             insert_postgres(msg_dict) 
          # will look like this
          # {"vote": "a", "voter_id": "71f0caa7172a84eb"}
          time.sleep(3)        
   
       except Exception as e:
          print(e)

if __name__ == '__main__':
    create_postgres_table()
    process_votes()
