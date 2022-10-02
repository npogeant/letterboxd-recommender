from itertools import chain

from re import U
from bs4 import BeautifulSoup
import requests
import json

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
else:
    from utils.get_user_preferred_movies import get_user_data
    from utils.get_popular_movies import get_popular_movies_this_week
    from utils.get_movie_data import get_movie_data
    from utils.recsys_model import import_data,data_preprocessing,get_recommendations

tmdb_key = (os.getenv('API_KEY'))

def generate_user_data(username):
    user_data = get_user_data(username)
    
    with open('data/user_movies.txt', 'w') as f:
        for movie in user_data:
            f.write(f"{movie}\n")
    
    if len(user_data) >= 72:
        user_data = user_data[:72]
    else:
        pass
    
    user_tmdb_data = get_movie_data(user_data)

    df = pd.DataFrame(user_tmdb_data)
    nan_value = float("NaN")
    df.replace("", nan_value, inplace=True)
    df.dropna(subset = ["genres"], inplace=True)
    df.to_csv('data/user_tmdb_data.csv', index=None)
    
def generate_popular_movies_data():
    popular_movies_data = get_popular_movies_this_week()

    popular_movies_poster = json.dumps(popular_movies_data)
    with open('data/popular_movies_poster.json', 'w') as f:
        f.write(popular_movies_poster)

    popular_movies_list = [movie_object['movie_id'] for movie_object in popular_movies_data]
    popular_movies_tmdb_data = get_movie_data(popular_movies_list)

    df = pd.DataFrame(popular_movies_tmdb_data)
    df.to_csv('data/popular_movies_tmdb_data.csv', index=None)
    
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