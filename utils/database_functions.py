import os 

from dotenv import load_dotenv
load_dotenv()

import sqlalchemy as db
from sqlalchemy.dialects.postgresql import insert as pg_insert

url = (os.getenv('DB_CONNECTION'))

def create_DB_connection(url):
    '''
    Initialiaze DB connection
    
    Args:
      - url : elephant url for connection
      
    Returns:
      - connection : engine.raw_connection()
      - engine : create_engine sql alchemy conncetion
    '''
    
    engine = db.create_engine(url)
    connection = engine.raw_connection()
    metadata = db.MetaData()
    print("Connection with the database established .........")
    return connection, engine, metadata
  
def close_DB_connection(connection, engine):
    '''
    Close DB connection
    
    Args:
      - connection : engine.raw_connection()
      - engine : create_engine sql alchemy conncetion
    '''
    
    connection.commit()
    connection.close()
    engine.dispose()
    print("........ Connection with the database closed")
  
def send_popular_movies_to_DB(data):
    '''
    Send dict of popular movies from Letterboxd to a Postgresql DB.
    
    Args:
      - data : popular movies dictionary
    '''
  
    connection, engine, metadata = create_DB_connection(url)

    insp = db.inspect(engine)
    if insp.has_table("popular_movies", schema="public") == False:
      
      # Create popular_movies table
      popular_movies = db.Table(
          'popular_movies', metadata, 
          db.Column('movie_id', db.String, primary_key = True), 
          db.Column('image_url', db.String),
      )
      popular_movies.create(engine)
      
      # Insert movies
      insert_stmt = pg_insert(popular_movies)
      for movie in data:
          try :
            engine.execute(insert_stmt, movie)
          except Exception as e:
            if e == 'IntegrityError':
                print('The movie is already in the table.')
                pass
    else:
      # Initialize popular_movies table metadata
      popular_movies = db.Table('popular_movies', 
                                metadata, 
                                autoload=True, 
                                autoload_with=engine, 
                                schema='public')
      
      # Insert movies
      insert_stmt = pg_insert(popular_movies)
      for movie in data:
          try :
            engine.execute(insert_stmt, movie)
          except Exception as e:
            if e == 'IntegrityError':
                print('The movie is already in the table.')
                pass

    close_DB_connection(connection, engine)
    
def get_popular_movies_from_DB():
    '''
    Get dict of popular movies from Letterboxd stored in a Postgresql DB.
    
    Returns:
      - popular_movies_data : popular movies dictionary
    '''
    
    connection, engine, metadata = create_DB_connection(url)


    popular_movies = db.Table('popular_movies', 
                        metadata, 
                        autoload=True, 
                        autoload_with=engine, 
                        schema='public')

    popular_movies_data = engine.execute(db.select(*popular_movies.c)).fetchall()

    close_DB_connection(connection, engine)

    return popular_movies_data