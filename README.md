# Movie Recommender System - Python & Letterboxd [![web app](https://img.shields.io/badge/streamlit-letterboxd_recsys-blue?style=flat-square)](https://npogeant-letterboxd-recommender-web-app-hyud2u.streamlitapp.com/) [![article](https://medium.com/mlearning-ai/python-letterboxd-build-a-content-filtering-rec-sys-from-scratch-7648b25bccdc)]()
> A Content Based Filtering Recommender System on Letterboxd Movies

The idea of this application is to provide **recommendations** of popular movies based on a user tastes.

## The Data

Data used to build the model are scraped movies information from a user diary of **Letterboxd** and scraped [popular movies from the week](https://letterboxd.com/films/popular/this/week/).

Those data are enhanced with features collected from [The Movie Database (TMDB) API](https://www.themoviedb.org/documentation/api?language=fr-FR).

## The Model

Once the data preprocessed, the **model** computes cosine similarities between each movie. As it is a content based filtering, the idea is to have recommendations by comparing movie to movie. The model returns the 5 closest movies to the user profile.

## The Web App

The web app is hosted on **Streamlit** which is one of the best platforms to create web applications. The app consists of a form with a single input: the Letterboxd username. Once entered, submitted, the form calls the user data scraping function and then runs the recommendation system by calculating the similarity between user profiles and popular movies.

This is an example of the [**web application**](https://npogeant-letterboxd-recommender-web-app-hyud2u.streamlitapp.com/) : 

<p align="center">
  <img src="utils/image/web_app.gif" alt="App Example" width="738">
</p>