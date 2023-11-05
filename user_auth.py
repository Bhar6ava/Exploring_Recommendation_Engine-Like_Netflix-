from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import psycopg2

#app = Flask(__name__)
app = Flask(__name__, static_url_path='/static')

# Configure your database settings here
db_settings = {
    "dbname": "capstone_netflix",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost"
}

# Define a secret key for session management
app.secret_key = "your_secret_key"






# Define a function to establish a database connection
def connect_to_database():
    return psycopg2.connect(**db_settings)

# Define routes and views

# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # Verify user credentials in the database
        if verify_user(username, password):
            session["username"] = username
            
            #return redirect(url_for("movies"))
            #return render_template("movies.html")
            return redirect(url_for("movies"))
            #return "success"
        else:
            return render_template("login.html",error = "User does not exist. Please create an account")
            #return "User does not exist. Please create an account."
            #return redirect(url_for("login"))
            #render_template("login.html")

    return render_template("login.html")

# Create an account page
@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # Add user to the database
        if create_user(username, password):
            #return redirect(url_for("login"))
            return "success"
        else:
            return "Failed to create an account. Please try again."

    return render_template("create_account.html")

# Movie content page (requires user authentication)
# Function to fetch movie data
def fetch_movie_data():
    conn = psycopg2.connect(**db_settings)
    cursor = conn.cursor()

    # Execute a SQL query to fetch movie data
    cursor.execute("SELECT name, description, genre, thumbnail_path FROM movies")

    # Fetch all rows from the result set
    movie_data = cursor.fetchall()

    # Create a dictionary to organize movies by genre
    organized_movies = {}
    for movie in movie_data:
        name, description, genre, thumbnail_url = movie
        if genre not in organized_movies:
            organized_movies[genre] = []
        if len(organized_movies[genre]) < 7: 
            organized_movies[genre].append((name, description, genre, thumbnail_url))

    # Close the database connection
    conn.close()

    return organized_movies


@app.route("/movies")
def movies(): 
    # Fetch movie data from the database
    movie_data = fetch_movie_data()

    # Render the HTML template and pass the movie data
    return render_template("movies12.html", movie_data=movie_data)



# REST API endpoint to fetch movie details by title
@app.route("/movie/<string:name>", methods=["GET"])
def get_movie_details(name):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(**db_settings)
    cursor = conn.cursor()

    # Query the database for movie details based on the title
    cursor.execute(
        "SELECT description FROM movies WHERE name = %s", (name,)
    )
    movie_details = cursor.fetchone()
    print("desc")
    print(movie_details)
    print(type(movie_details))
    # Close the database connection
    cursor.close()
    conn.close()

    return jsonify(description = movie_details[0]) , 200

    


# Function to verify user credentials
def verify_user(username, password):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_auth WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# Function to create a new user account
def create_user(username, password):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_auth (username, password) VALUES (%s, %s)", (username, password))
    conn.commit()
    conn.close()
    return True

if __name__ == "__main__":
    app.run(debug=True)


    
