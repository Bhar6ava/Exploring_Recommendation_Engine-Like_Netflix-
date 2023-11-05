import requests
from bs4 import BeautifulSoup
import psycopg2
import os

#npm install --save movie-trailer
def scrape_imdb_data(genre, num_movies=25):
    url = f"https://www.imdb.com/search/title/?genres={genre}&sort=num_votes,desc&count={num_movies}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    movies = []
    for movie in soup.find_all("div", class_="lister-item-content"):
        print(movie)
        m_name = movie.find("h3").a.text.strip()
        description = movie.find_all("p", class_="text-muted")[-1].text.strip()
        #thumbnail_url = movie.find("img")["src"]

        a_tag = movie.find_previous("a")
        if a_tag and a_tag.has_attr("href"):
            name = a_tag["href"]
            img_tag = a_tag.find("img")
            thumbnail_url = img_tag["loadlate"] if img_tag and img_tag.has_attr("loadlate") else "No thumbnail available"


        # Download the thumbnail and store it in a folder
        #thumbnail_path = f"thumbnails/{m_name.replace(' ','_')}.jpg"
        #os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
        #with open(thumbnail_path, "wb") as img_file:
        #    img_file.write(requests.get(thumbnail_url).content)

        # Prepare movie data
        movie_data = {
            "name": m_name,
            "genre": genre,
            "description": description,
            #"thumbnail_path": thumbnail_path,
            #"youtube_link": youtube_link
        }
        movies.append(movie_data)

    return movies

# Example usage:
if __name__ == "__main__":
    # Specify genres and the number of movies to scrape
    genres = ["comedy"]
    num_movies_per_genre = 25

    # Scrape and insert data for each genre
    for genre in genres:
        movies = scrape_imdb_data(genre, num_movies_per_genre)
        