import json

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

from modules import init, MODELS, FEATURES
from modules.table_utils import import_data
init()

POST_REC_PATH = "/recommend"

def recommend_item(username):

    name = 'similarity_model'

    logging.info('Importing data...')
    user_tmdb_data, popular_movies_tmdb_data, popular_movies_poster = import_data(username)

    logging.info('Building the model...')
    model = MODELS[name]

    encoder = FEATURES.get(model.FEATURES)
    res = encoder.preprocess(user_tmdb_data, popular_movies_tmdb_data)

    logging.info('Performing recommendations...')
    top_n_rec = model.fit(res['data'])

    mv = popular_movies_tmdb_data.set_index('movie_id').to_dict('index')

    rec_name = [res['movie_ids'][rec] for rec in top_n_rec]
    rec_title = [mv[name]['movie_title'] for name in rec_name]
    rec_date = [mv[name]['release_date'][:4] for name in rec_name]
    rec_image = [poster['image_url'] for name in rec_name for poster in popular_movies_poster if poster['movie_id'] == name]    

    return {"movies": rec_name,
            "title": rec_title,
            "date": rec_date,
            "images": rec_image}

def handler(event, context):
    try:
        # Validate event structure
        if 'rawPath' not in event or 'body' not in event:
            return {"error": "Invalid request structure"}

        if event['rawPath'] == POST_REC_PATH:
            logging.info('Received a request to /recommend')

            # Parse the request body
            body = event['body']   
            if not body:
                return {"error": "Request body is empty"}

            # Convert the body to JSON format
            try:
                body_json = json.loads(body)
            except json.JSONDecodeError:
                return {"error": "Invalid JSON in request body"}

            # Validate required parameters
            if 'username' not in body_json:
                return {"error": "Username not provided"}

            username = body_json['username']

            # Call the recommendation function
            result = recommend_item(username)

            logging.info('Here are the recommendations...')

            return result
        else:
            return {"error": "Unsupported path"}
    except Exception as e:
        logging.error(f"Error in handler: {str(e)}")
        return {"error": "Internal server error"}