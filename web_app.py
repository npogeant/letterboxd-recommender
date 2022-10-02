import streamlit as st
from PIL import Image

import json, base64

from pipeline import generate_user_data,generate_popular_movies_data,get_top_5_recommendations

# Add a background
@st.experimental_memo
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_img_as_base64("utils/image/background.png")

page_bg_img = f"""
                <style>
                [data-testid="stAppViewContainer"] > .main {{
                background-image: url("data:image/png;base64,{img}");
                background-position: top left;
                background-repeat: no-repeat;
                background-attachment: local;
                -webkit-background-size: cover;
                -moz-background-size: cover;
                -o-background-size: cover;
                background-size: cover;
                }}
                [data-testid="stForm"] {{
                background: rgb(14, 17, 23) none repeat scroll 0% 0%;
                border: none;
                }}
                </style>"""

st.markdown(page_bg_img, unsafe_allow_html=True)

# Create the title
st.markdown(
    "<h1 style='text-align: center; color: white;'>Letterboxd Popular Movies Recommender</h1>",
    unsafe_allow_html=True,
)

# Add the logos
empty1, logo1, empty2, logo2, empty3 = st.columns(5)

with empty1:
    st.text('')
    
with logo1:
    st.text('')
    image = Image.open('utils/image/letterboxd_logo.png')
    st.image(image)
    
with empty2:
    st.text('')
    
with logo2:
    st.text('')
    image = Image.open('utils/image/tmdb_logo.png')
    st.image(image)
    
with empty3:
    st.text('')

# Add paragraphs
st.markdown(
    "<h3 style='text-align: center; color: grey;'>Get 5 recommendations based on your Letterboxd diary</h1>",
    unsafe_allow_html=True,
)

st.markdown('''<p style='text-align: center;'>The recommendations come from Letterboxd popular movies this week that you can find <a style="text-decoration: none; color: white" href="https://letterboxd.com/films/popular/this/week//" 
            target="_blank" rel="noopener noreferrer"><ins>here</ins></a>.</p>''',
            unsafe_allow_html=True)

# Build the form containing all the username
with st.form("my_form"):
    username = st.text_input(
        'Give a valid Letterboxd username (the one from the URL)', value=''
    )

    submitted = st.form_submit_button("Submit")


def predict(username):
    """
    A function that generates the user data, popular movies, builds and then
    returns the recommendations.
    Args:
        - username : a valid Letterboxd username
    """
    
    generate_user_data(username)
    generate_popular_movies_data()
    recommendations = get_top_5_recommendations()

    return recommendations

def open_util_files():
    """
    A function that opens some useful files.
    """
    
    with open('data/popular_movies_poster.json') as f:
        popular_movies_poster = f.read()
    popular_movies_poster = json.loads(popular_movies_poster)

    with open('data/user_movies.txt') as f:
        movies = f.read().splitlines()
        
    return popular_movies_poster, movies

# This function returns a success answer if everything goes right
def main():
    if submitted:
        with st.spinner("Getting recommendations..."):
                try:
                    prediction = predict(username)
                    popular_movies_poster, movies = open_util_files()
                    st.success(f"Here are your recommendations based on {len(movies)} movies watched 😎 :")
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        # st.header(prediction[0].strip('-').capitalize())
                        image_url = [poster['image_url'] for poster in popular_movies_poster if poster['movie_id'] == prediction[0]][0]
                        image_url = image_url.replace('70-0-105', '125-0-187')
                        st.markdown(f"[![Foo](https://a.ltrbxd.com/resized/{image_url}.jpg)](https://letterboxd.com/film/{prediction[0]}/)")
                        movie_title = f'''<p><a style="text-decoration: none; color: white" href="https://letterboxd.com/film/{prediction[0]}/" 
                        target="_blank" rel="noopener noreferrer">{prediction[0].replace('-', ' ').capitalize()}</a></p>'''
                        st.markdown(movie_title, unsafe_allow_html=True)

                    with col2:
                        # st.header(prediction[1].strip('-').capitalize())
                        image_url = [poster['image_url'] for poster in popular_movies_poster if poster['movie_id'] == prediction[1]][0]
                        image_url = image_url.replace('70-0-105', '125-0-187')
                        st.markdown(f"[![Foo](https://a.ltrbxd.com/resized/{image_url}.jpg)](https://letterboxd.com/film/{prediction[1]}/)")
                        movie_title = f'''<p><a style="text-decoration: none; color: white" href="https://letterboxd.com/film/{prediction[1]}/" 
                        target="_blank" rel="noopener noreferrer">{prediction[1].replace('-', ' ').capitalize()}</a></p>'''
                        st.markdown(movie_title, unsafe_allow_html=True)

                    with col3:
                        # st.header(prediction[2].strip('-').capitalize())
                        image_url = [poster['image_url'] for poster in popular_movies_poster if poster['movie_id'] == prediction[2]][0]
                        image_url = image_url.replace('70-0-105', '125-0-187')
                        st.markdown(f"[![Foo](https://a.ltrbxd.com/resized/{image_url}.jpg)](https://letterboxd.com/film/{prediction[2]}/)")
                        movie_title = f'''<p><a style="text-decoration: none; color: white" href="https://letterboxd.com/film/{prediction[2]}/" 
                        target="_blank" rel="noopener noreferrer">{prediction[2].replace('-', ' ').capitalize()}</a></p>'''
                        st.markdown(movie_title, unsafe_allow_html=True)

                    with col4:
                        # st.header(prediction[3].strip('-').capitalize())
                        image_url = [poster['image_url'] for poster in popular_movies_poster if poster['movie_id'] == prediction[3]][0]
                        image_url = image_url.replace('70-0-105', '125-0-187')
                        st.markdown(f"[![Foo](https://a.ltrbxd.com/resized/{image_url}.jpg)](https://letterboxd.com/film/{prediction[3]}/)")
                        movie_title = f'''<p><a style="text-decoration: none; color: white" href="https://letterboxd.com/film/{prediction[3]}/" 
                        target="_blank" rel="noopener noreferrer">{prediction[3].replace('-', ' ').capitalize()}</a></p>'''
                        st.markdown(movie_title, unsafe_allow_html=True)
                        
                    with col5:
                        # st.header(prediction[4].strip('-').capitalize())
                        image_url = [poster['image_url'] for poster in popular_movies_poster if poster['movie_id'] == prediction[4]][0]
                        image_url = image_url.replace('70-0-105', '125-0-187')
                        st.markdown(f"[![Foo](https://a.ltrbxd.com/resized/{image_url}.jpg)](https://letterboxd.com/film/{prediction[4]}/)")
                        movie_title = f'''<p><a style="text-decoration: none; color: white" href="https://letterboxd.com/film/{prediction[4]}/" 
                        target="_blank" rel="noopener noreferrer">{prediction[4].replace('-', ' ').capitalize()}</a></p>'''
                        st.markdown(movie_title, unsafe_allow_html=True)
                        
                except Exception as e:  # pylint: disable=broad-except
                    print(e)
                    st.warning('The username does not exist... or no movies are in the diary 😳')

if __name__ == "__main__":
    main()