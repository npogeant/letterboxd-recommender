from itertools import chain

from re import U
from bs4 import BeautifulSoup
import requests
import json, time

import asyncio
from aiohttp import ClientSession

import pandas as pd

from pprint import pprint

from dotenv import load_dotenv
load_dotenv()

import os
if os.getcwd().endswith("/utils"):
    from get_user_preferred_films import get_user_data # type: ignore
    from get_popular_movies import get_popular_movies_this_week # type: ignore
    from get_movie_data import get_movie_data # type: ignore
    from recsys_model import import_data,data_preprocessing,get_recommendations # type: ignore
    from database_functions import get_popular_movies_from_DB # type: ignore
else:
    from utils.get_user_preferred_movies import get_user_data
    from utils.get_popular_movies import get_popular_movies_this_week
    from utils.get_movie_data import get_movie_data
    from utils.recsys_model import import_data,data_preprocessing,get_recommendations
    from utils.database_functions import get_popular_movies_from_DB 

tmdb_key = (os.getenv('API_KEY'))

def generate_user_data(username):
    user_data = get_user_data(username)
    
    with open('data/user_movies.txt', 'w') as f:
        for movie in user_data:
            f.write(f"{movie}\n")
            
    print("User movies txt saved...")
    
    if len(user_data) >= 72:
        user_data = user_data[:72]
    else:
        pass
    
    user_tmdb_data = get_movie_data(user_data)
    
    print("User movies tmdb data generated...")

    df = pd.DataFrame(user_tmdb_data)
    nan_value = float("NaN")
    df.replace("", nan_value, inplace=True)
    df.dropna(subset = ["genres"], inplace=True)
    df.to_csv('data/user_tmdb_data.csv', index=None)
    
    print("User movies tmdb data saved...")
    
def generate_popular_movies_data(data_from_db=True):
    
    if data_from_db == False:
        popular_movies_data = get_popular_movies_this_week()
    else:
        popular_movies_data = get_popular_movies_from_DB()
        
    popular_movies_data = [dict(movie_tuple) for movie_tuple in popular_movies_data]

    popular_movies_poster = json.dumps(popular_movies_data)
    with open('data/popular_movies_poster.json', 'w') as f:
        f.write(popular_movies_poster)
        
    print("Popular movies picture links saved...")

    popular_movies_list = [movie_object['movie_id'] for movie_object in popular_movies_data]

    popular_movies_tmdb_data = []
    if len(popular_movies_list) > 100:
        for i in range(0, len(popular_movies_list), 50):
            popular_movies_tmdb_data += get_movie_data(popular_movies_list[i:i+50])
            
    print(len(popular_movies_tmdb_data))

    print("Popular movies data generated...")

    df = pd.DataFrame(popular_movies_tmdb_data)
    df.to_csv('data/popular_movies_tmdb_data.csv', index=None)
    
    print("Popular movies data saved...")
    
def get_top_5_recommendations():
    user_tmdb_data, popular_movies_tmdb_data = import_data('data/user_movies.txt', 'data/user_tmdb_data.csv', 'data/popular_movies_tmdb_data.csv')
    concat_data = data_preprocessing(user_tmdb_data, popular_movies_tmdb_data)
    top_five_recommendations_id = get_recommendations(concat_data)
    print(top_five_recommendations_id)
    
    return top_five_recommendations_id

if __name__ == '__main__':
    generate_user_data('oxlade8')
    generate_popular_movies_data()
    get_top_5_recommendations()