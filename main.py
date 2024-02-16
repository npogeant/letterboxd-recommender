from modules import init, MODELS, MODEL_LIBRARIES, FEATURES
from modules.table_utils import import_data
init()

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():

    name = 'similarity_model'

    user_tmdb_data, popular_movies_tmdb_data = import_data('./data/user_movies.txt', './data/user_tmdb_data.csv', './data/popular_movies_tmdb_data.csv')

    model = MODELS[name]

    encoder = FEATURES.get(model.FEATURES)
    res = encoder.preprocess(user_tmdb_data, popular_movies_tmdb_data)

    top_n_rec = model.fit(res['data'])

    return {"reco": [res['movie_ids'][rec] for rec in top_n_rec]}