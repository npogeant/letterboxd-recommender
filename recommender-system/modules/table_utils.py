
import pandas as pd
import numpy as np

import json

import boto3

from ast import literal_eval

# import nltk
# existing_nltk_data_path = "/modules/nltk_data"
# nltk.data.path.append(existing_nltk_data_path)
# from nltk.corpus import stopwords

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer

import os
if os.getcwd().endswith("/modules"):
    from utils.get_user_preferred_movies import get_user_data
    from utils.get_movie_data import get_movie_data
else:
    from .utils.get_user_preferred_movies import get_user_data
    from .utils.get_movie_data import get_movie_data

def safe_literal_eval(val):
    try:
        return literal_eval(val)
    except (ValueError, SyntaxError):
        return val  # return the original value if it can not be evaluated

def import_data(username):

    # User data
    user_data = get_user_data(username)
    movies = [movie['movie_id'] for movie in user_data]
    user_data = [movie['movie_id'] for movie in user_data if movie['rating_val'] > 7]
    if len(user_data) >= 72:
        user_data = user_data[:72]
    else:
        pass
    
    # User TMDB data
    user_tmdb_data = get_movie_data(user_data)
    user_tmdb_data = pd.DataFrame(user_tmdb_data)
    nan_value = float("NaN")
    user_tmdb_data.replace("", nan_value, inplace=True)
    user_tmdb_data.dropna(subset = ["genres"], inplace=True)

    # AWS Session
    session = boto3.Session()
    s3 = session.client('s3')
    bucket_name = 'letterboxd-recsys'
    key_csv = 'data/Popular movies data.csv'
    key_json = 'data/Popular movies poster.json'

    # Popular movie data
    obj = s3.get_object(Bucket=bucket_name, Key=key_csv)
    popular_movies_tmdb_data = pd.read_csv(obj['Body'])
    # popular_movies_tmdb_data = pd.read_csv(csv_popular_movies_tmdb_data, converters={'genres': safe_literal_eval})
    already_seen_movies = list((set(popular_movies_tmdb_data['movie_id']).intersection(movies)))
    popular_movies_tmdb_data = popular_movies_tmdb_data[~popular_movies_tmdb_data['movie_id'].str.contains('|'.join(already_seen_movies))]
    
    # Popular movie posters
    obj = s3.get_object(Bucket=bucket_name, Key=key_json)
    popular_movies_poster = json.loads(obj['Body'].read())

    return user_tmdb_data, popular_movies_tmdb_data, popular_movies_poster

def get_user_preferred_genre(user_data):

    genres = ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Mystery', 'Romance', 'Science Fiction',
    'Thriller', 'TV Movie', 'War', 'Western']

    one_hot_genres = user_data['genres'].str.join('|').str.get_dummies()

    difference = list((set(genres).difference(one_hot_genres)))

    if len(difference) > 0:
        for genre in difference :
            one_hot_genres[genre] = 0
            # print(genre + ' added !')
        one_hot_genres = one_hot_genres[genres]
    else:
        # print('Nothing added !')
        one_hot_genres = one_hot_genres[genres]
        
    most_preferred_genre_array = np.where(one_hot_genres.sum()*2 > one_hot_genres.sum().max(), 1,0)
    user_preferred_genre = pd.DataFrame([most_preferred_genre_array], columns=genres)

    return user_preferred_genre

def get_user_preferred_decade(user_data):

    user_data['decade'] = user_data['year_released'] - user_data['year_released'].astype(str).str[-1].astype(int)

    most_preferred_decade = user_data['decade'].value_counts().idxmax()
    user_preferred_decade = pd.DataFrame([most_preferred_decade], columns=['decade'])

    return user_preferred_decade

def get_user_preferred_language(user_data):

    most_preferred_lang = user_data['original_language'].value_counts().idxmax()
    user_preferred_language = pd.DataFrame([most_preferred_lang], columns=['original_language'])

    return user_preferred_language

def get_user_preferred_length(user_data):

    most_preferred_length = int(user_data['runtime'].mean())
    user_preferred_length = pd.DataFrame([most_preferred_length], columns=['runtime'])

    return user_preferred_length

def get_user_reconstituted_overview(user_data):

    # Initialize a TF-IDF Vectorizer whose vectors size is 5000 and
    # composed by the main unigrams and bigrams found in the corpus
    vectorizer = TfidfVectorizer(analyzer='word',
                        ngram_range=(1, 2),
                        min_df=0.003,
                        max_df=0.5,
                        max_features=5000)

    tfidf_matrix = vectorizer.fit_transform(user_data['overview']) # fit and transform overviews
    tfidf_feature_names = vectorizer.get_feature_names_out() # get feature names from the transformed vectorizer

    df = pd.DataFrame(tfidf_matrix.toarray(), columns = tfidf_feature_names) # gather data and feature names

    # Keep the 50 best tokens
    top_50_overview_tokens = df.sum().reset_index(None).rename(columns={'index':'token', 0:'tfidf_sum'}).sort_values(by='tfidf_sum', ascending=False).head(50)

    # Reconstitute an overview based on the best tokens
    most_relevant_tokens = ' '.join(top_50_overview_tokens['token'])
    user_reconstituted_overview = pd.DataFrame([most_relevant_tokens], columns=['overview'])

    return user_reconstituted_overview
