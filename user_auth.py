from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import psycopg2, requests

#app = Flask(__name__)
app = Flask(__name__, static_url_path='/static')


db_settings = {
    "dbname": "capstone_netflix",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost"
}


app.secret_key = "your_secret_key"


add_recommendations = 'yes'

user_recom = ''




def connect_to_database():
    return psycopg2.connect(**db_settings)







@app.route("/login", methods=["GET", "POST"])
def login():

    global user_recom

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        if verify_user(username, password):
            session["username"] = username
            
            #return redirect(url_for("movies"))
            #return render_template("movies.html")
            #return redirect(url_for("movies"))

            if add_recommendations == 'yes':
                data = {"user_id":username}
                user_recom = data.get("user_id")
                return redirect(url_for("movies_recommend"))

            else:
                return redirect(url_for("movies"))
            #return "success"
        else:
            return render_template("login.html",error = "User does not exist. Please create an account")
            #return "User does not exist. Please create an account."
            #return redirect(url_for("login"))
            #render_template("login.html")

    return render_template("login.html")


@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        if create_user(username, password):
            #return redirect(url_for("login"))
            return "success"
        else:
            return "Failed to create an account. Please try again."

    return render_template("create_account.html")



def fetch_movie_data():
    conn = psycopg2.connect(**db_settings)
    cursor = conn.cursor()

    
    cursor.execute("SELECT name, description, genre, thumbnail_path FROM movies")

    
    movie_data = cursor.fetchall()

    
    organized_movies = {}
    for movie in movie_data:
        name, description, genre, thumbnail_url = movie
        if genre not in organized_movies:
            organized_movies[genre] = []
        if len(organized_movies[genre]) < 7: 
            organized_movies[genre].append((name, description, genre, thumbnail_url))

    
    conn.close()

    return organized_movies

def recommended_movie_info(movie_recom):
    conn = psycopg2.connect(**db_settings)
    cursor = conn.cursor()
    print("inside")
    print(movie_recom)

    movie_recom_list = []

    for i in movie_recom:
        print(i[0])
        cursor.execute("SELECT name, description, genre, thumbnail_path FROM movies WHERE name = %s", (i[0],))
        movie_data = cursor.fetchall()  
        if movie_data:
            movie_recom_list.append(movie_data[0])

    return movie_recom_list

@app.route("/movies/recommend", methods=['GET'])
def movies_recommend():
    
    conn = psycopg2.connect(**db_settings)
    cursor = conn.cursor()

    cursor.execute("SELECT preference_id FROM user_auth WHERE username = %s", (user_recom,))
    preference_id = cursor.fetchone()[0]

    cursor.execute("SELECT movies FROM recommendations WHERE user_id = %s", (preference_id,))
    movie_recom = cursor.fetchall()

    movie_recom_list = recommended_movie_info(movie_recom[-7:])
    #print(movie_recom_list)

    movie_data = fetch_movie_data()

    return render_template("movies20.html", movie_data=movie_data, movie_recom=movie_recom_list)

@app.route("/movies",methods=['GET'])
def movies(): 

    movie_data = fetch_movie_data()

    
    return render_template("movies19.html", movie_data=movie_data)



@app.route("/track_click", methods=["POST"])
def track_click():
    try:

        if request.method == 'OPTIONS':
            
            response = jsonify()
            response.headers['Access-Control-Allow-Methods'] = 'POST'
            return response

        
        data = request.get_json()
        print(data)
        action = data.get("buttonClicked")
        movie_title = data.get("movieTitle")
        print(movie_title)
        username = data.get("username")  

        
        value = 0
        if action == "More":
            value = 1
        elif action == "Play Trailer":
            value = 2
        elif action == "Watched":
            value = 3
        
        conn = psycopg2.connect(**db_settings)
        
        cursor = conn.cursor()

        
        cursor.execute("SELECT preference_id FROM user_auth WHERE username = %s", (username,))
        preference_id = cursor.fetchone()[0]
        print(preference_id)

        
        cursor.execute(f"SELECT \"{movie_title.replace(' ', '_')}\" FROM preference_matrix WHERE user_id = %s", (preference_id,))
        current_value = cursor.fetchone()[0]
        print(current_value)

        if current_value == None:
            current_value = 0
        
        if value > current_value:
            print("inside")
            
            cursor.execute(f"UPDATE preference_matrix SET \"{movie_title.replace(' ', '_')}\" = %s WHERE user_id = %s", (value, preference_id))
            
            conn.commit()

        
        cursor.close()
        conn.close()

        return jsonify(success=True), 200
        

    except Exception as e:
        return jsonify(error=str(e)), 500



@app.route("/movie/<string:name>", methods=["GET"])
def get_movie_details(name):
    
    conn = psycopg2.connect(**db_settings)
    cursor = conn.cursor()

    
    cursor.execute(
        "SELECT description FROM movies WHERE name = %s", (name,)
    )
    movie_details = cursor.fetchone()
    print("desc")
    print(movie_details)
    print(type(movie_details))
    
    cursor.close()
    conn.close()

    return jsonify(description = movie_details[0]) , 200

    



def verify_user(username, password):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_auth WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None


def create_user(username, password):
    conn = connect_to_database()
    cursor = conn.cursor()

    
    cursor.execute("INSERT INTO preference_matrix DEFAULT VALUES RETURNING user_id")
    preference_id = cursor.fetchone()[0]

    
    cursor.execute("INSERT INTO user_auth (username, password, preference_id) VALUES (%s, %s, %s)", (username, password, preference_id))


    conn.commit()
    conn.close()
    return True



@app.route("/movie/recommend/", methods=["POST"])
def recom_movies():

    conn = psycopg2.connect(**db_settings)
    cursor = conn.cursor()

    data = request.get_json()
    print(data)

    user_id = data.get('user_id')
    recom_movies = data.get('recommended_movie_names')
    print(user_id)
    print(recom_movies)


    for movie in recom_movies:
        cursor.execute('''
            INSERT INTO recommendations (user_id, movies)
            VALUES (%s, %s)
        ''', (user_id, movie))

    conn.commit()
    return jsonify({"message": "Recommendations inserted successfully."})


if __name__ == "__main__":
    app.run(debug=True)


    
