import pandas as pd
import numpy as np

import requests

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Embedding, Concatenate, Dense, Input, Flatten

import psycopg2

# %%
db_settings = {
    "dbname": "capstone_netflix",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost"
}

conn = psycopg2.connect(**db_settings)

df = pd.read_sql('select * from preference_matrix', conn)


conn.close()

df_original = df.fillna(0)

df_original

num_synthetic_users = 1000



df_synthetic = pd.DataFrame({'user_id': range(8, 1008)})



for movie_col in df_original.columns[1:]:
    df_synthetic[movie_col] = np.random.randint(4, size=len(df_synthetic))


df = pd.concat([df_original, df_synthetic], ignore_index=True)



df.dropna(inplace=True)

df


user_col = 'user_id'
movie_cols = df.columns[1:]


interaction_matrix = df.set_index(user_col)[movie_cols]


interaction_matrix_normalized = interaction_matrix / 3.0


train_data, test_data = train_test_split(interaction_matrix_normalized, test_size=0.2, random_state=42)


def build_model(num_users, num_movies, embedding_size=50):
    user_input = Input(shape=(1,))
    movie_input = Input(shape=(1,))

    user_embedding = Embedding(input_dim=num_users, output_dim=embedding_size)(user_input)
    movie_embedding = Embedding(input_dim=num_movies, output_dim=embedding_size)(movie_input)

    user_flatten = Flatten()(user_embedding)
    movie_flatten = Flatten()(movie_embedding)

    concat = Concatenate()([user_flatten, movie_flatten])
    dense1 = Dense(100, activation='relu')(concat)
    dense2 = Dense(50, activation='relu')(dense1)
    output = Dense(1, activation='sigmoid')(dense2)

    model = Model(inputs=[user_input, movie_input], outputs=output)
    model.compile(optimizer='adam', loss='mean_squared_error')
    
    return model


num_users = df[user_col].nunique()
num_movies = len(movie_cols)

model = build_model(num_users, num_movies)




user_ids, movie_ids = np.where(train_data.notna())
X_train = [user_ids, movie_ids]
y_train = train_data.values[train_data.notna()]


model.fit(X_train, y_train, epochs=10, batch_size=64, validation_split=0.2)


user_ids_test, movie_ids_test = np.where(test_data.notna())
X_test = [user_ids_test, movie_ids_test]
y_test = test_data.values[test_data.notna()]



predictions = model.predict(X_test)


mse = mean_squared_error(y_test, predictions)
print(f"Mean Squared Error: {mse}")



user_id = 6  


interacted_movies = interaction_matrix.loc[user_id][interaction_matrix.loc[user_id] < 3].index

recommendations_df = pd.DataFrame({
    'movie_id': interaction_matrix.columns,
    'predicted_rating': model.predict([np.full(len(interaction_matrix.columns), user_id), np.arange(len(interaction_matrix.columns))]).flatten()})


top_recommendations = recommendations_df.nlargest(7, 'predicted_rating')


print(top_recommendations)


recom = recommendations_df.sort_values(by='predicted_rating', ascending=False)


recom

recommended_movies = list(recom['movie_id'][:7])
recommended_movies = [movie.replace('_', ' ') for movie in recommended_movies]

recommended_movies = list(set(recommended_movies))
print(recommended_movies)



endpoint_url = "http://127.0.0.1:5000/movie/recommend/"


data = {"user_id" : user_id,"recommended_movie_names": recommended_movies}



response = requests.post(endpoint_url, json=data)
print(response.status_code)
