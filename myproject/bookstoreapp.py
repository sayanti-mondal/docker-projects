# from flask import Flask, render_template, request, redirect, url_for

# # Initialize the Flask application
# app = Flask(__name__)

# # --- Main Route ---
# # Serves the initial page (index.html)
# @app.route('/')
# def home():
#     """Renders the main bookstore landing page."""
#     # Flask automatically looks for 'index.html' inside the 'templates' folder
#     return render_template('index.html')

# # --- Login Submission Route ---
# @app.route('/login', methods=['POST'])
# def login():
#     """Handles the login form submission."""
#     # Retrieve form data
#     email = request.form.get('email')
#     password = request.form.get('password')

#     # In a real app, you would validate credentials against a database here.
#     print(f"\n--- LOGIN ATTEMPT ---")
#     print(f"Email: {email}")
#     print(f"Password: {password}")
#     print("-----------------------\n")

#     # Placeholder success message (redirecting back to home for simplicity)
#     # You would typically redirect to a user dashboard.
#     return render_template('index.html', message="Login successful for " + email + "!")

# # --- Signup Submission Route ---
# @app.route('/signup', methods=['POST'])
# def signup():
#     """Handles the signup form submission."""
#     # Retrieve form data
#     full_name = request.form.get('full_name')
#     email = request.form.get('email')
#     password = request.form.get('password')

#     # In a real app, you would hash the password and save the user to a database here.
#     print(f"\n--- SIGNUP ATTEMPT ---")
#     print(f"Full Name: {full_name}")
#     print(f"Email: {email}")
#     print(f"Password: {password}")
#     print("------------------------\n")

#     # Placeholder success message (redirecting back to home for simplicity)
#     return render_template('index.html', message="Signup successful! Welcome, " + full_name + "!")

# # --- Run the application ---
# if __name__ == '__main__':
#     # Setting debug=True allows for automatic reloading on code changes
#     app.run(host='0.0.0.0', port=5000)

# # Note: The index.html file must be placed inside a 'templates' folder.



from flask import Flask, render_template, request
import pymysql.cursors
import os
import time

# Initialize the Flask application
app = Flask(__name__)

# --- Database Connection Details from Environment Variables ---

# These variables are injected by the 'web' service in docker-compose.yml
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'db') # 'db' is the hostname of the database service
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_ROOT_PASSWORD', 'example_root_password')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'bookstoredb')

# --- Database Setup Functions ---

def get_db_connection():
    """Attempts to establish a connection to the MySQL database with retries."""
    max_retries = 5
    retry_delay = 5  # seconds
    
    for i in range(max_retries):
        try:
            # Connect to the MySQL server
            conn = pymysql.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
                cursorclass=pymysql.cursors.DictCursor
            )
            print("Successfully connected to MySQL.")
            return conn
        except pymysql.err.OperationalError as e:
            if i < max_retries - 1:
                print(f"Database not ready. Retrying in {retry_delay}s... (Attempt {i+1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                print(f"Failed to connect to MySQL after {max_retries} attempts.")
                raise e

def init_db():
    """Initializes the database by creating the users table if it doesn't exist."""
    print("Initializing database...")
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Note: In a real-world application, you MUST store HASHED passwords, not plain text.
            # Use a library like Flask-Bcrypt for proper hashing.
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    full_name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            ''')
        conn.commit()
    except Exception as e:
        print(f"Error during database initialization: {e}")
    finally:
        if 'conn' in locals() and conn.open:
            conn.close()
    print("Database initialization complete.")

# Ensure the database is initialized when the application starts
with app.app_context():
    init_db()

# --- Main Route ---

@app.route('/')
def home():
    """Renders the main bookstore landing page."""
    return render_template('index.html')

# --- Login Submission Route ---

@app.route('/login', methods=['POST'])
def login():
    """Handles the login form submission by checking credentials against the database."""
    email = request.form.get('email')
    password = request.form.get('password')
    message = "Login failed. Invalid email or password."
    conn = None

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # For this simple demo, we check plaintext. In production, use HASHING.
            sql = "SELECT full_name FROM users WHERE email = %s AND password = %s"
            cursor.execute(sql, (email, password))
            user = cursor.fetchone()

            if user:
                message = f"Login successful! Welcome back, {user['full_name']}."
            
    except Exception as e:
        message = f"An unexpected database error occurred during login: {e}"

    finally:
        if conn and conn.open:
            conn.close()

    return render_template('index.html', message=message)

# --- Signup Submission Route ---

@app.route('/signup', methods=['POST'])
def signup():
    """Handles the signup form submission by creating a new user in the database."""
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    password = request.form.get('password')
    message = ""
    conn = None

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Before insertion, in a real app, you would HASH the password.
            sql = "INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)"
            cursor.execute(sql, (full_name, email, password))
        conn.commit()
        message = f"Signup successful! Welcome, {full_name}. You can now log in."

    except pymysql.err.IntegrityError as e:
        # Handles duplicate email (UNIQUE constraint violation)
        if 'Duplicate entry' in str(e):
            message = "Signup failed: An account with this email already exists."
        else:
            message = f"An unexpected database error occurred during signup: {e}"

    except Exception as e:
        message = f"An unexpected error occurred during signup: {e}"

    finally:
        if conn and conn.open:
            conn.close()

    return render_template('index.html', message=message)

# --- Run the application ---
if __name__ == '__main__':
    # Running with '0.0.0.0' makes it accessible inside the Docker network
    app.run(host='0.0.0.0', port=5000, debug=True)

# REMINDER: For production, ensure you use password hashing and secure user sessions!

