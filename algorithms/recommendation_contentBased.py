import pandas as pd
import numpy as np
from PIL import Image

import os
import requests

import psycopg2

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Flatten, Dense

from tensorflow.keras.applications import VGG16
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array

from tensorflow.keras.preprocessing import image
import numpy as np

from tensorflow.keras.layers import Concatenate

db_settings = {
    "dbname": "capstone_netflix",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost"
}

conn = psycopg2.connect(**db_settings)

movies_df = pd.read_sql('select name,description from movies', conn)


movies_df

tokenizer = Tokenizer(num_words=1000, oov_token="<OOV>")
tokenizer.fit_on_texts(movies_df['description'].astype(str).tolist())
sequences = tokenizer.texts_to_sequences(movies_df['description'].astype(str).tolist())
padded_sequences = pad_sequences(sequences, maxlen=100, padding='post', truncating='post')

label_encoder = LabelEncoder()
labels = label_encoder.fit_transform(movies_df['name'])

X_train, X_test, y_train, y_test = train_test_split(padded_sequences, labels, test_size=0.2, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(padded_sequences, labels, test_size=0.2, random_state=42)

nlp_model = Sequential()
nlp_model.add(Embedding(input_dim=1000, output_dim=16, input_length=100))
nlp_model.add(Flatten())
nlp_model.add(Dense(64, activation='relu'))
nlp_model.add(Dense(len(label_encoder.classes_), activation='softmax'))

nlp_model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
nlp_model.fit(X_train, y_train, epochs=50, validation_data=(X_test, y_test))

thumbnail_folder = '/Users/dev/cap_netflix_tensor/thumb/thumbnails/'
image_features_list = []

base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
i=0

for filename in os.listdir(thumbnail_folder):
    i=i+1
    print(i)
    try:
        image_path = os.path.join(thumbnail_folder, filename)
        img = Image.open(image_path)
        img = img.resize((224, 224))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        features = base_model.predict(img_array)

        image_features_list.append(features)

    except Exception as e:
        print(f"Error processing image {filename}: {e}")

image_features = np.concatenate(image_features_list, axis=0)

image_features_flat = image_features.reshape((image_features.shape[0], -1))

image_model = Sequential()
image_model.add(Dense(256, activation='relu', input_dim=image_features_flat.shape[1]))
image_model.add(Dense(len(label_encoder.classes_), activation='softmax'))

image_model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
image_model.fit(image_features_flat, labels, epochs=50, validation_split=0.2)

nlp_output = nlp_model.layers[-2].output 
image_output = image_model.layers[-2].output

combined = Concatenate()([nlp_output, image_output])

combined_model = Sequential()
combined_model.add(Dense(256, activation='relu', input_dim=204))
combined_model.add(Dense(len(label_encoder.classes_), activation='softmax'))

combined_model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

df = pd.read_sql('select * from preference_matrix', conn)
user_col = 'user_id'
movie_cols = df.columns[1:]

interaction_matrix = df.set_index(user_col)[movie_cols]

interacted_movies = interaction_matrix.loc[user_id][(interaction_matrix.loc[user_id] < 3) & (interaction_matrix.loc[user_id] > 0)].index
print(interacted_movies)

recommended_movies = []

for i in interacted_movies:
    print(i)
    new_description = pd.read_sql('select description from movies where name='+"'"+i.replace('_',' ')+"'"+' LIMIT 1', conn)
    new_description = str(new_description.iloc[0]['description'])
    print(new_description)

    new_thumbnail_path = "thumb/thumbnails/"+i+".jpg"

    new_description_sequence = tokenizer.texts_to_sequences([new_description])
    new_padded_sequence = pad_sequences(new_description_sequence, maxlen=100, padding='post', truncating='post')

    new_thumbnail = image.load_img(new_thumbnail_path, target_size=(224, 224))
    new_thumbnail_array = image.img_to_array(new_thumbnail)
    new_thumbnail_array = np.expand_dims(new_thumbnail_array, axis=0)
    new_thumbnail_array /= 255.0 
    
    nlp_prediction = nlp_model.predict(new_padded_sequence)

    image_features = base_model.predict(new_thumbnail_array)
    image_features_flat = image_features.reshape((image_features.shape[0], -1))

    image_prediction = image_model.predict(image_features_flat)

    combined_input = np.concatenate([nlp_prediction, image_prediction], axis=1)

    combined_input = combined_input.reshape((combined_input.shape[0], 204))

    combined_prediction = combined_model.predict(combined_input)

    predicted_movie_index = np.argmax(combined_prediction)
    predicted_movie_name = label_encoder.classes_[predicted_movie_index]

    predicted_movie_indices = np.argsort(combined_prediction[0])[::-1][:5]
    predicted_movie_names = label_encoder.classes_[predicted_movie_indices]

    print("Predicted Movie Name:", predicted_movie_names)
    
    recommended_movies.extend(predicted_movie_names)

conn.close()

recommended_movies = list(set(recommended_movies))
print(recommended_movies)


endpoint_url = "http://127.0.0.1:5000/movie/recommend/"

data = {"user_id" : user_id,"recommended_movie_names": recommended_movies[:7]}

response = requests.post(endpoint_url, json=data)
print(response.status_code)

