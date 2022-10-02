from itertools import chain

from re import U
from bs4 import BeautifulSoup
import requests

import asyncio
from aiohttp import ClientSession

from pprint import pprint

from dotenv import load_dotenv
load_dotenv()

import os

tmdb_key = (os.getenv('API_KEY'))

async def fetch(url, session, input_data={}):
    async with session.get(url) as r:
        response = await r.read()

        # Parse ratings page response for each rating/review, use lxml parser for speed
        soup = BeautifulSoup(response, "lxml")
        
        movie_header = soup.find('section', attrs={'id': 'featured-film-header'})

        try:
            movie_title = movie_header.find('h1').text
        except AttributeError:
            movie_title = ''

        try:
            year = int(movie_header.find('small', attrs={'class': 'number'}).find('a').text)
        except AttributeError:
            year = None

        try:
            imdb_link = soup.find("a", attrs={"data-track-action": "IMDb"})['href']
            imdb_id = imdb_link.split('/title')[1].strip('/').split('/')[0]
        except:
            imdb_link = ''
            imdb_id = ''

        try:
            tmdb_link = soup.find("a", attrs={"data-track-action": "TMDb"})['href']
            tmdb_id = tmdb_link.split('/movie')[1].strip('/').split('/')[0]
        except:
            tmdb_link = ''
            tmdb_id = ''
        
        movie_object = {
                    "movie_id": input_data["movie_id"],
                    "movie_title": movie_title,
                    "year_released": year,
                    "imdb_id": imdb_id,
                    "tmdb_id": tmdb_id
                }

        return movie_object
      
async def get_movies(movie_list):
    url = "https://letterboxd.com/film/{}/"
    
    async with ClientSession() as session:
        # print("Starting Scrape", time.time() - start)

        tasks = []
        # Make a request for each ratings page and add to task queue
        for movie in movie_list:
            task = asyncio.ensure_future(fetch(url.format(movie), session, {"movie_id": movie}))
            tasks.append(task)

        # Gather all ratings page responses
        movies_response = await asyncio.gather(*tasks)
        
        return movies_response
    
async def fetch_tmdb_data(url, session, movie_data, input_data={}):
    async with session.get(url) as r:
        response = await r.json()

        movie_object = movie_data

        object_fields = ["genres", "production_countries", "spoken_languages"]
        for field_name in object_fields:
            try:
                movie_object[field_name] = [x["name"] for x in response[field_name]]
            except:
                movie_object[field_name] = None
        
        simple_fields = ["popularity", "overview", "runtime", "vote_average", "vote_count", "release_date", "original_language"]
        for field_name in simple_fields:
            try:
                movie_object[field_name] = response[field_name]
            except:
                movie_object[field_name] = None

        return movie_object
    
async def get_rich_data(movie_list):
    base_url = "https://api.themoviedb.org/3/movie/{}?api_key={}"

    async with ClientSession() as session:

        tasks = []
        movie_list = [x for x in movie_list if x['tmdb_id']]
        # Make a request for each ratings page and add to task queue
        for movie in movie_list:
            # print(base_url.format(movie["tmdb_id"], tmdb_key))
            task = asyncio.ensure_future(fetch_tmdb_data(base_url.format(movie["tmdb_id"], tmdb_key), session, movie, {"movie_id": movie["movie_id"]}))
            tasks.append(task)

        # Gather all ratings page responses
        infos_responses = await asyncio.gather(*tasks)
        
        return infos_responses
      
      
def get_movie_data(movie_list):
  
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(get_movies(movie_list))
    loop.run_until_complete(future)
    movies_response_list = future.result()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(get_rich_data(movies_response_list))
    loop.run_until_complete(future)

    return future.result()
      
if __name__ == '__main__':
    get_movie_data(['skyfall', 'spider-man-2'])