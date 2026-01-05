from flask import Flask, render_template, request, redirect, session, abort, jsonify, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = 'secret123'

# -------------------- DB INIT --------------------
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT UNIQUE,
        password TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        rating INTEGER,
        message TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

# -------------------- ROUTES --------------------

@app.route('/')
def index():
    if 'user' in session:
        return redirect('/home')
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[3], password):
            session['user'] = user[1]
            return redirect('/home')
        else:
            return "Login failed. Invalid username or password."
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                      (username, email, hashed_pw))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "Email already registered."
        conn.close()
        session['user'] = username
        return redirect('/login')
    return render_template('signup.html')

@app.route('/home')
def home():
    if 'user' in session:
        return render_template('home.html', username=session['user'])
    return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# ---------- STORYWORLD ----------
@app.route('/storyworld')
def storyworld():
    return render_template('storyworld.html')

@app.route('/storyworld/<animal>')
def play_animal_video(animal):
    videos = {
        'rabbit': 'rabbit.mp4',
        'bear': 'bear.mp4',
        'lion': 'lion.mp4',
        'monkey': 'monkey.mp4',
        'deer': 'deer.mp4',
        'zebra': 'zebra.mp4'
    }
    video_file = videos.get(animal)
    if video_file:
        return render_template('play_video.html', video_file=video_file)
    else:
        return "Animal not found", 404

# ---------- FEEDBACK ----------
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        rating = request.form.get('rating')
        message = request.form.get('message')
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO feedback (name, email, rating, message) VALUES (?, ?, ?, ?)",
                  (name, email, rating, message))
        conn.commit()
        conn.close()
        return '''
        <html>
          <head>
            <title>Thank You!</title>
            <style>
              body {
                font-family: 'Comic Sans MS', cursive;
                background: #e0f7fa;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                text-align: center;
                flex-direction: column;
              }
              h2 {
                font-size: 2rem;
                color: #4b0082;
              }
              .confetti {
                font-size: 3rem;
                animation: pop 0.8s ease infinite alternate;
              }
              @keyframes pop {
                from { transform: scale(1); }
                to { transform: scale(1.2); }
              }
              a {
                margin-top: 20px;
                text-decoration: none;
                color: #3366cc;
                font-weight: bold;
              }
            </style>
          </head>
          <body>
            <div class="confetti">🎉🎊✨</div>
            <h2>Thank you for your feedback!</h2>
            <a href="/home">← Back to Home</a>
          </body>
        </html>
        '''
    return render_template("feedback.html")

# ---------- ADMIN DASHBOARD ----------
@app.route('/admin/feedback')
def view_feedback():
    if session.get("user") != "admin":
        return "Access Denied 👮", 403
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id, name, email, rating, message FROM feedback ORDER BY id DESC")
    feedback_list = c.fetchall()
    conn.close()
    return render_template('admin_feedback.html', feedback=feedback_list)

@app.route('/admin/delete-feedback', methods=['POST'])
def delete_feedback():
    if session.get("user") != "admin":
        return "Access Denied", 403
    feedback_id = request.form.get("id")
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM feedback WHERE id = ?", (feedback_id,))
    conn.commit()
    conn.close()
    return redirect('/admin/feedback')

@app.route('/science')
def science_games():
    return render_template('science_games.html')

@app.route('/science/float-sink')
def float_sink_game():
    return render_template('float_sink.html')

@app.route('/science/element-friends')
def element_friends():
    elements = [
        {"name": "Hydrogen", "symbol": "H", "color": "#f2f2f2", "superpower": "Loves to bond!", "fun_fact": "It's the lightest element."},
        {"name": "Helium", "symbol": "He", "color": "#ffcccb", "superpower": "Floats up high!", "fun_fact": "Used in balloons."},
        {"name": "Lithium", "symbol": "Li", "color": "#c4f0c5", "superpower": "Zaps batteries!", "fun_fact": "Found in rechargeable batteries."},
        {"name": "Beryllium", "symbol": "Be", "color": "#b3e6ff", "superpower": "Stays super strong!", "fun_fact": "Used in aerospace materials."},
        {"name": "Boron", "symbol": "B", "color": "#ffdfba", "superpower": "Glass fixer!", "fun_fact": "Used in borosilicate glass."},
        {"name": "Carbon", "symbol": "C", "color": "#404040", "superpower": "Builds life!", "fun_fact": "Found in all living things."},
        {"name": "Nitrogen", "symbol": "N", "color": "#b0e0e6", "superpower": "Puts out fire!", "fun_fact": "Most of the air is nitrogen."},
        {"name": "Oxygen", "symbol": "O", "color": "#87cefa", "superpower": "Helps breathe!", "fun_fact": "Essential for respiration."},
        {"name": "Fluorine", "symbol": "F", "color": "#e6e6fa", "superpower": "Fights tooth decay!", "fun_fact": "Used in toothpaste."},
        {"name": "Neon", "symbol": "Ne", "color": "#f08080", "superpower": "Glows bright!", "fun_fact": "Used in neon signs."},
        {"name": "Sodium", "symbol": "Na", "color": "#ffff99", "superpower": "Makes salty sparks!", "fun_fact": "Reacts explosively with water!"},
        {"name": "Magnesium", "symbol": "Mg", "color": "#d3ffce", "superpower": "Shines in flares!", "fun_fact": "Burns with a bright white light."},
        {"name": "Aluminum", "symbol": "Al", "color": "#e6e6e6", "superpower": "Light and strong!", "fun_fact": "Used in cans and airplanes."},
        {"name": "Silicon", "symbol": "Si", "color": "#f0e68c", "superpower": "Tech builder!", "fun_fact": "Used in computer chips."},
        {"name": "Phosphorus", "symbol": "P", "color": "#ffa07a", "superpower": "Glows in dark!", "fun_fact": "Used in matches."},
        {"name": "Sulfur", "symbol": "S", "color": "#ffff00", "superpower": "Stinky power!", "fun_fact": "Smells like rotten eggs."},
        {"name": "Chlorine", "symbol": "Cl", "color": "#98fb98", "superpower": "Cleans pools!", "fun_fact": "Kills germs in water."},
        {"name": "Argon", "symbol": "Ar", "color": "#dda0dd", "superpower": "Keeps lights glowing!", "fun_fact": "Used in light bulbs."},
        {"name": "Potassium", "symbol": "K", "color": "#ffe4b5", "superpower": "Firecracker!", "fun_fact": "Explodes in water."},
        {"name": "Calcium", "symbol": "Ca", "color": "#fffacd", "superpower": "Bone builder!", "fun_fact": "Strengthens teeth and bones."},
        {"name": "Scandium", "symbol": "Sc", "color": "#b0c4de", "superpower": "Light yet mighty!", "fun_fact": "Used in sports gear."},
        {"name": "Titanium", "symbol": "Ti", "color": "#c0c0c0", "superpower": "Tough and shiny!", "fun_fact": "Used in implants."},
        {"name": "Vanadium", "symbol": "V", "color": "#d8bfd8", "superpower": "Stops rust!", "fun_fact": "Added to steel."},
        {"name": "Chromium", "symbol": "Cr", "color": "#add8e6", "superpower": "Shiny armor!", "fun_fact": "Used in chrome plating."},
        {"name": "Manganese", "symbol": "Mn", "color": "#f5deb3", "superpower": "Steel booster!", "fun_fact": "Improves steel strength."},
        {"name": "Iron", "symbol": "Fe", "color": "#cd5c5c", "superpower": "Builds bridges!", "fun_fact": "Core of Earth is iron."},
        {"name": "Cobalt", "symbol": "Co", "color": "#6495ed", "superpower": "Blue painter!", "fun_fact": "Used in blue glass."},
        {"name": "Nickel", "symbol": "Ni", "color": "#a9a9a9", "superpower": "Coin maker!", "fun_fact": "Used in batteries and coins."},
        {"name": "Copper", "symbol": "Cu", "color": "#b87333", "superpower": "Electric hero!", "fun_fact": "Great conductor of electricity."},
        {"name": "Zinc", "symbol": "Zn", "color": "#dcdcdc", "superpower": "Stops rust!", "fun_fact": "Used to galvanize steel."}
    ]
    return render_template('element_friends.html', elements=elements)


@app.route('/maths')
def maths():
    return render_template('maths.html')

@app.route('/add-game')
def add_game():
    return render_template('add_game.html')

@app.route('/sub-game')
def sub_game():
    return render_template('sub_game.html')

@app.route('/mul-game')
def mul_game():
    return render_template('mul_game.html')

@app.route('/div-game')
def div_game():
    return render_template('div_game.html')

@app.route('/world-explorer')
def world_explorer():
    return render_template('world_explorer.html')

@app.route('/world/india')
def india_page():
    return render_template('india.html')

@app.route('/india/food')
def india_food():
    return render_template('india_food.html')

@app.route('/india/culture')
def india_culture():
    return render_template('india_culture.html')

@app.route('/india/wildlife')
def india_wildlife():
    # Renders the Wildlife Passport game you built
    return render_template('wildlife_passport_india.html')

@app.route('/world/australia')
def australia_redirect():
    return render_template('australia_intro.html')

# Koala's Culture Trail Page
@app.route('/koalas-culture-trail')
def koalas_culture_trail():
    return render_template('koalas_culture_trail.html')

@app.route('/world/japan')
def japan_page():
    return render_template('japan_intro.html')  # 🌸 Japan intro page (region selector)

@app.route('/japan/tokyo')
def japan_tokyo():
    return render_template('japan_tokyo.html')  # 🍱 Tokyo region with mini-games

@app.route('/japan/kyoto')
def japan_kyoto():
    return render_template('japan_kyoto.html')  # 🎎 Kyoto region with cultural games

@app.route('/japan/hokkaido')
def japan_hokkaido():
    return render_template('japan_hokkaido.html')  # 🐾 Hokkaido region with wildlife games

# ---------- RUN ----------
if __name__ == '__main__':
    app.run(debug=True)
