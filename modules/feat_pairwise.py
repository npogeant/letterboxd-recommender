import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from modules.table_utils import (
    get_user_preferred_genre, 
    get_user_preferred_decade, 
    get_user_preferred_language, 
    get_user_preferred_length, 
    get_user_reconstituted_overview
)
class FeatureEncoder():

    NAME = 'pairwise'
    FEATURE_LIBRARIES = {}
    CLEAN_FIELDS = ['trip_distance', 'total_amount']
    
    @classmethod
    def preprocess(cls, user_tmdb_data, popular_movies_tmdb_data):
        
        user_movie_id = pd.DataFrame(['user-profile-recsys'], columns=['movie_id']) 
        user_preferred_decade = get_user_preferred_decade(user_tmdb_data)
        user_reconstituted_overview = get_user_reconstituted_overview(user_tmdb_data)
        user_preferred_length = get_user_preferred_length(user_tmdb_data)
        user_preferred_language = get_user_preferred_language(user_tmdb_data)
        user_preferred_genre = get_user_preferred_genre(user_tmdb_data)

        user_profile = pd.concat([user_movie_id, user_preferred_decade, user_reconstituted_overview, user_preferred_length, user_preferred_language, user_preferred_genre], axis=1)
        
        popular_movies_tmdb_data = popular_movies_tmdb_data.dropna(subset=['overview']).copy() # drop rows with NaN values in the overview column
        
        popular_movies_tmdb_data['decade'] = popular_movies_tmdb_data['year_released'] - popular_movies_tmdb_data['year_released'].astype(str).str[-1].astype(int)

        genres = ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Mystery', 'Romance', 'Science Fiction',
        'Thriller', 'TV Movie', 'War', 'Western']

        one_hot_genres = popular_movies_tmdb_data['genres'].str.join('|').str.get_dummies()

        difference = list((set(genres).difference(one_hot_genres)))

        if len(difference) > 0:
            for genre in difference :
                one_hot_genres[genre] = 0
                # print(genre + ' added !')
            one_hot_genres = one_hot_genres[genres]
        else:
            # print('Nothing added !')
            one_hot_genres = one_hot_genres[genres]
            
        one_hot_genres

        popular_movies = pd.concat([popular_movies_tmdb_data[['movie_id', 'decade', 'overview', 'runtime', 'original_language']], one_hot_genres], axis=1)
        
        concat_data = pd.concat([user_profile, popular_movies], axis=0)
        data = concat_data.reset_index(drop=True)

        tfidf_vectorizer = TfidfVectorizer()
        doc_vec = tfidf_vectorizer.fit_transform(data.iloc[:,2]) # overview text tf-idf
        
        label_encoder = LabelEncoder()
        data['decade'] = label_encoder.fit_transform(data['decade'])
        
        
        original_language = data['original_language'].str.get_dummies()
        
        data = pd.concat([data, original_language], axis=1)
        
        movie_ids = data['movie_id'].to_dict()
        
        data = data.drop(['movie_id', 'overview', 'original_language'], axis=1)
        
        min_max_scaler = MinMaxScaler()
        data = pd.DataFrame(min_max_scaler.fit_transform(data), columns=data.columns)

        return {
            'data': data,
            'movie_ids': movie_ids
        }
