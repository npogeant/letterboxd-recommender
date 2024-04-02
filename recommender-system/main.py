import logging
from flask import Flask, request, jsonify
from modules import init, MODELS, FEATURES
from modules.table_utils import import_data

# Initialize Flask application
app = Flask(__name__)

# Initialize logger
logging.basicConfig(level=logging.INFO)

# Initialize your application
init()

# Define endpoint path
POST_REC_PATH = "/recommend"

# Function to perform recommendations
def recommend_item(username):
    name = 'similarity_model'

    # Import data
    user_tmdb_data, popular_movies_tmdb_data, popular_movies_poster = import_data(username)

    # Build the model
    model = MODELS[name]

    encoder = FEATURES.get(model.FEATURES)
    res = encoder.preprocess(user_tmdb_data, popular_movies_tmdb_data)

    # Perform recommendations
    top_n_rec = model.fit(res['data'])

    mv = popular_movies_tmdb_data.set_index('movie_id').to_dict('index')

    rec_name = [res['movie_ids'][rec] for rec in top_n_rec]
    rec_title = [mv[name]['movie_title'] for name in rec_name]
    rec_date = [mv[name]['release_date'][:4] for name in rec_name]
    rec_image = [poster['image_url'] for name in rec_name for poster in popular_movies_poster if poster['movie_id'] == name]    

    return {
        "movies": rec_name,
        "title": rec_title,
        "date": rec_date,
        "images": rec_image
    }

@app.route('/')
def test():
    return "Hello World"

# Define endpoint handler
@app.route(POST_REC_PATH, methods=['POST'])
def get_recommendation():
    try:
        # Parse request body
        body = request.json
        if not body:
            return jsonify({"error": "Request body is empty"}), 400

        # Validate required parameters
        if 'username' not in body:
            return jsonify({"error": "Username not provided"}), 400

        username = body['username']

        # Call the recommendation function
        result = recommend_item(username)

        # Return recommendations
        return jsonify(result), 200

    except Exception as e:
        logging.error(f"Error in handler: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Main function
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
