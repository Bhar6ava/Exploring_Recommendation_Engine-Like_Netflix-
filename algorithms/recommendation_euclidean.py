import pandas as pd
import psycopg2
import requests

db_settings = {
    "dbname": "capstone_netflix",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost"
}

conn = psycopg2.connect(**db_settings)

df = pd.read_sql('SELECT * FROM preference_matrix', conn)

df = df.fillna(0)

user_id_column = 'user_id'
user_data = df.drop(columns=[user_id_column])

given_user_id = 1  

given_user_index = df[df[user_id_column] == given_user_id].index[0]

def euclidean_distance(row1, row2):
    return sum((row1 - row2)**2)**0.5


distances_to_given_user = user_data.apply(lambda row: euclidean_distance(row, user_data.iloc[given_user_index]), axis=1)




similar_users_df = pd.DataFrame({
    'user_id': df[user_id_column],
    'euclidean_distance': distances_to_given_user
})


similar_users_df = similar_users_df.sort_values(by='euclidean_distance', ascending=False)


print(similar_users_df)


top_similar_users = similar_users_df.head(3)

given_user_row = df[df[user_id_column] == given_user_id].iloc[0]


recommended_movies = []
for user in top_similar_users['user_id']:
    similar_user_row = df[df[user_id_column] == user].iloc[0]
    for movie in user_data.columns:
        if given_user_row[movie] < 3 and similar_user_row[movie] == 3:
            recommended_movies.append(movie)


print("Recommended Movies:", recommended_movies)


recommended_movies = list(recom['movie_id'][:7])
recommended_movies = [movie.replace('_', ' ') for movie in recommended_movies]

recommended_movies = list(set(recommended_movies))
print(recommended_movies)


endpoint_url = "http://127.0.0.1:5000/movie/recommend/"


data = {"user_id" : user_id,"recommended_movie_names": recommended_movies}


response = requests.post(endpoint_url, json=data)
print(response.status_code)
