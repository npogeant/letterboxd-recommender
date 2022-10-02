import pandas as pd
import numpy as np

from ast import literal_eval

import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity

def import_data(text_user_movies, csv_user_tmdb_data, csv_popular_movies_tmdb_data):
    with open(text_user_movies) as f:
        movies = f.read().splitlines()
        
    user_tmdb_data = pd.read_csv(csv_user_tmdb_data, converters={'genres': literal_eval})

    popular_movies_tmdb_data = pd.read_csv(csv_popular_movies_tmdb_data, converters={'genres': literal_eval})
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


def data_preprocessing(user_tmdb_data, popular_movies_tmdb_data):
    
    user_movie_id = pd.DataFrame(['user-profile-recsys'], columns=['movie_id'])
    user_preferred_decade = get_user_preferred_decade(user_tmdb_data)
    user_reconstituted_overview = get_user_reconstituted_overview(user_tmdb_data)
    user_preferred_length = get_user_preferred_length(user_tmdb_data)
    user_preferred_language = get_user_preferred_language(user_tmdb_data)
    user_preferred_genre = get_user_preferred_genre(user_tmdb_data)

    user_profile = pd.concat([user_movie_id, user_preferred_decade, user_reconstituted_overview, user_preferred_length, user_preferred_language, user_preferred_genre], axis=1)
    
    
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
    concat_data = concat_data.reset_index(drop=True)

    return concat_data

def final_preprocessing(data):
  
    tfidf_vectorizer = TfidfVectorizer()
    doc_vec = tfidf_vectorizer.fit_transform(data.iloc[:,2]) # overview text tf-idf
    
    # Compute the dot product/cross product between user-profile-recsys and all othe movies
    # which is the cosine similarities of each pair of vectors
    overview_cosine_similarities = cosine_similarity(doc_vec[0:1], doc_vec).flatten()
    data['overview_similarty_user_vs_popular'] = overview_cosine_similarities
    
    label_encoder = LabelEncoder()
    data['decade'] = label_encoder.fit_transform(data['decade'])
    
    
    original_language = data['original_language'].str.get_dummies()
    
    data = pd.concat([data, original_language], axis=1)
    
    movie_id = data['movie_id'].to_dict()
    
    data = data.drop(['movie_id', 'overview', 'original_language'], axis=1)
    
    min_max_scaler = MinMaxScaler()
    data = pd.DataFrame(min_max_scaler.fit_transform(data), columns=data.columns)

    return data, movie_id


def get_recommendations(data):
    vectorized_data, movie_id = final_preprocessing(data)
    top_five_recommendations = cosine_similarity(vectorized_data.iloc[0:1], vectorized_data.iloc[:]).argsort()[0][-6:-1]
    top_five_recommendations_id = [movie_id[rec] for rec in top_five_recommendations]
    top_five_recommendations_id.reverse()
    
    return top_five_recommendations_id

if __name__ == '__main__':
    user_tmdb_data, popular_movies_tmdb_data = import_data('../data/user_movies.txt', '../data/user_tmdb_data.csv', '../data/popular_movies_tmdb_data.csv')
    concat_data = data_preprocessing(user_tmdb_data, popular_movies_tmdb_data)
    top_five_recommendations_id = get_recommendations(concat_data)
    print(top_five_recommendations_id)
    