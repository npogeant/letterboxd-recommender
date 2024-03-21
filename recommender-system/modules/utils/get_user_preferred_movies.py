from itertools import chain

from re import U
from bs4 import BeautifulSoup
import requests

import asyncio
from aiohttp import ClientSession

from pprint import pprint

import os

async def fetch(url, session, input_data={}):
    async with session.get(url) as response:
        return await response.read(), input_data
      
def get_page_count(username):
    url = "https://letterboxd.com/{}/films/by/date"
    r = requests.get(url.format(username))

    soup = BeautifulSoup(r.text, "lxml")
    
    body = soup.find("body")
    if "error" in body["class"]:
        return -1, None

    try:
        page_link = soup.findAll("li", attrs={"class", "paginate-page"})[-1]
        num_pages = int(page_link.find("a").text.replace(',', ''))
    except IndexError:
        num_pages = 1

    return num_pages

async def generate_ratings_operations(response, return_unrated=False):
    
    # Parse ratings page response for each rating/review, use lxml parser for speed
    soup = BeautifulSoup(response[0], "lxml")
    reviews = soup.findAll("li", attrs={"class": "poster-container"})

    # Create empty array to store list of bulk operations or rating objects
    ratings_operations = []

    # For each review, parse data from scraped page and append an UpdateOne operation for bulk execution or a rating object
    for review in reviews:
        movie_id = review.find('div', attrs={"class", "film-poster"})['data-target-link'].split('/')[-2]

        rating = review.find("span", attrs={"class": "rating"})
        if not rating:
            if return_unrated == False:
                continue
            else:
                rating_val = -1
        else:
            rating_class = rating['class'][-1]
            rating_val = int(rating_class.split('-')[-1])
      
        rating_object = {
                    "movie_id": movie_id,
                    "rating_val": rating_val,
                    "user_id": response[1]["username"]
                }

        ratings_operations.append(rating_object)
    
    return ratings_operations
  
async def get_user_ratings(username, num_pages=None, return_unrated=False):
    url = "https://letterboxd.com/{}/films/by/member-rating/page/{}/"

    # Fetch all responses within one Client session,
    # keep connection alive for all requests.
    async with ClientSession() as session:
        tasks = []
        # Make a request for each ratings page and add to task queue
        for i in range(num_pages):
            task = asyncio.ensure_future(fetch(url.format(username, i+1), session, {"username": username}))
            tasks.append(task)
        # Gather all ratings page responses
        scrape_responses = await asyncio.gather(*tasks)
        
    # Process each ratings page response, converting it into bulk upsert operations or output dicts
    tasks = []
    for response in scrape_responses:
        task = asyncio.ensure_future(generate_ratings_operations(response, return_unrated=return_unrated))
        tasks.append(task)
    
    parse_responses = await asyncio.gather(*tasks)

    # Concatenate each response's upsert operations/output dicts
    upsert_ratings_operations = []
    for response in parse_responses:
        upsert_ratings_operations += response
        
    return upsert_ratings_operations
  
def get_user_data(username):
    num_pages = get_page_count(username)
    
    if num_pages == -1:
        return [], "user_not_found"

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(get_user_ratings(username, num_pages=num_pages, return_unrated=True))
    loop.run_until_complete(future)

    # user_movie_list = [movie['movie_id'] for movie in future.result()]

    return future.result()

if __name__ == '__main__':
  user_movie_list = get_user_data('oxlade8')
  print([movie['movie_id'] for movie in user_movie_list if movie['rating_val'] > 7])