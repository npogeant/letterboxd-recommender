
import pandas as pd
import numpy as np

from ast import literal_eval

import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer

def safe_literal_eval(val):
    try:
        return literal_eval(val)
    except (ValueError, SyntaxError):
        return val  # return the original value if it can not be evaluated

def import_data(text_user_movies, csv_user_tmdb_data, csv_popular_movies_tmdb_data):
    with open(text_user_movies) as f:
        movies = f.read().splitlines()
        
    user_tmdb_data = pd.read_csv(csv_user_tmdb_data, converters={'genres': safe_literal_eval})

    popular_movies_tmdb_data = pd.read_csv(csv_popular_movies_tmdb_data, converters={'genres': safe_literal_eval})
    already_seen_movies = list((set(popular_movies_tmdb_data['movie_id']).intersection(movies)))
    popular_movies_tmdb_data = popular_movies_tmdb_data[~popular_movies_tmdb_data['movie_id'].str.contains('|'.join(already_seen_movies))]
    
    return user_tmdb_data, popular_movies_tmdb_data

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

    # Ignoring stopwords (words with no semantics) from English
    stopwords_list = stopwords.words('english')

    # Initialize a TF-IDF Vectorizer whose vectors size is 5000 and
    # composed by the main unigrams and bigrams found in the corpus, ignoring stopwords
    vectorizer = TfidfVectorizer(analyzer='word',
                        ngram_range=(1, 2),
                        min_df=0.003,
                        max_df=0.5,
                        max_features=5000,
                        stop_words=stopwords_list)

    tfidf_matrix = vectorizer.fit_transform(user_data['overview']) # fit and transform overviews
    tfidf_feature_names = vectorizer.get_feature_names_out() # get feature names from the transformed vectorizer

    df = pd.DataFrame(tfidf_matrix.toarray(), columns = tfidf_feature_names) # gather data and feature names

    # Keep the 50 best tokens
    top_50_overview_tokens = df.sum().reset_index(None).rename(columns={'index':'token', 0:'tfidf_sum'}).sort_values(by='tfidf_sum', ascending=False).head(50)

    # Reconstitute an overview based on the best tokens
    most_relevant_tokens = ' '.join(top_50_overview_tokens['token'])
    user_reconstituted_overview = pd.DataFrame([most_relevant_tokens], columns=['overview'])

    return user_reconstituted_overview
