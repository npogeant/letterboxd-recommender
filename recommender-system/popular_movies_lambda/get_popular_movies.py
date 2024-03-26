from bs4 import BeautifulSoup

import asyncio

from requests_html import AsyncHTMLSession

from pyppeteer import launch

import json

from get_movie_data import get_movie_data

import pandas as pd

import boto3


async def fetch(url, session):
    browser = await launch(
        {
            "ignoreHTTPSErrors": True,
            "headless": True,
            "handleSIGINT": False,
            "handleSIGTERM": False,
            "handleSIGHUP": False,
            "userDataDir": "/tmp",
        }
    )
    session._browser = browser
    page = await browser.newPage()
    await page.goto(url, {"timeout": 60000})
    response = session.get(url)
    return await response


async def generate_movies_operations(response):
    # Parse ratings page response for each rating/review, use lxml parser for speed
    await response.html.arender(wait=15, sleep=5)
    soup = BeautifulSoup(response.html.raw_html, "html.parser")

    movies = soup.findAll("li", attrs={"class": "listitem poster-container"})

    movie_operations = []

    for movie in movies:
        try:
            movie_id = movie.find("div", attrs={"class", "film-poster"})[
                "data-film-link"
            ].split("/")[-2]
        #   movie_id.append(next_id)
        except KeyError:
            movie_id = movie.find("div", attrs={"class", "film-poster"})[
                "data-target-link"
            ].split("/")[-2]
        #   movie_id.append(next_id)

        try:
            image_url = (
                movie.find("div", attrs={"class": "film-poster"})
                .find("img")["src"]
                .split("?")[0]
            )
            image_url = image_url.replace("https://a.ltrbxd.com/resized/", "").split(
                ".jpg"
            )[0]
            if "https://s.ltrbxd.com/static/img/empty-poster" in image_url:
                image_url = ""

        except AttributeError:
            image_url = ""

        movie_object = {"movie_id": movie_id, "image_url": image_url}

        movie_operations.append(movie_object)

    return movie_operations


async def get_popular_movies_id(num_pages=1):
    url = "https://letterboxd.com/films/popular/this/week/size/small/page/{}/"

    # Fetch all responses within one Client session,
    # keep connection alive for all requests.
    asession = AsyncHTMLSession()

    tasks = []
    # Make a request for each ratings page and add to task queue
    for i in range(num_pages):
        task = asyncio.ensure_future(fetch(url.format(i + 1), asession))
        tasks.append(task)
    # Gather all ratings page responses
    scrape_responses = await asyncio.gather(*tasks)

    tasks = []
    for response in scrape_responses:
        task = asyncio.ensure_future(generate_movies_operations(response))
        tasks.append(task)

    parse_responses = await asyncio.gather(*tasks)

    # Concatenate each response's upsert operations/output dicts
    upsert_ratings_operations = []
    for response in parse_responses:
        upsert_ratings_operations += response

    return upsert_ratings_operations


def get_popular_movies_this_week():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(get_popular_movies_id(num_pages=2))
    loop.run_until_complete(future)

    return future.result()


if __name__ == "__main__":
    # Get popular movies data
    popular_movies_data = get_popular_movies_this_week()

    # Convert to dictionary format
    popular_movies_data_dict = [
        dict(movie_tuple) for movie_tuple in popular_movies_data
    ]

    # Save as JSON
    with open("popular_movies_poster.json", "w") as f:
        json.dump(popular_movies_data_dict, f)

    # Extract movie IDs
    popular_movies_list = [
        movie_object["movie_id"] for movie_object in popular_movies_data_dict
    ]

    # Get TMDb data
    popular_movies_tmdb_data = []
    if len(popular_movies_list) > 0:
        for i in range(0, len(popular_movies_list), 50):
            popular_movies_tmdb_data += get_movie_data(popular_movies_list[i : i + 50])

    # Convert to DataFrame
    df = pd.DataFrame(popular_movies_tmdb_data)

    # Save as CSV
    df.to_csv("popular_movies_tmdb_data.csv", index=None)

    # Initialize the S3 client
    s3 = boto3.client("s3")

    bucket_name = "letterboxd-recsys"

    # Upload CSV file
    with open("popular_movies_tmdb_data.csv", "rb") as f:
        s3.upload_fileobj(f, bucket_name, "data/Popular movies data.csv")

    # Upload JSON file
    with open("popular_movies_poster.json", "rb") as f:
        s3.upload_fileobj(f, bucket_name, "data/Popular movies poster.json")
