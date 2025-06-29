from flask import Flask, request, redirect, render_template_string
import string, random, sqlite3
import os  # 👈 Added to read PORT from environment

app = Flask(__name__)

# SQLite DB setup
conn = sqlite3.connect('links.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS urls (short TEXT, original TEXT)''')
conn.commit()

# Short code generator
def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Main form and result page
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = request.form['url']
        short_code = generate_short_code()

        # Save to DB
        c.execute("INSERT INTO urls (short, original) VALUES (?, ?)", (short_code, original_url))
        conn.commit()

        # Use your actual domain in production
        short_url = f"{request.host_url}{short_code}"
        return render_template_string(TEMPLATE, short_url=short_url)

    return render_template_string(TEMPLATE)

# Redirect handler
@app.route('/<short_code>')
def redirect_url(short_code):
    c.execute("SELECT original FROM urls WHERE short=?", (short_code,))
    row = c.fetchone()
    if row:
        return redirect(row[0])
    else:
        return "Invalid URL", 404

# HTML + CSS template
TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>🔗 Simple Link Shortener</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background-color: #f4f4f4;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            flex-direction: column;
        }
        .container {
            background: white;
            padding: 2rem 3rem;
            border-radius: 12px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            text-align: center;
        }
        input[type="text"] {
            width: 80%;
            padding: 10px;
            font-size: 1rem;
            border: 2px solid #ddd;
            border-radius: 8px;
            margin-top: 1rem;
        }
        input[type="submit"] {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 1rem;
            margin-top: 1rem;
            border-radius: 8px;
            cursor: pointer;
        }
        .result {
            margin-top: 1.5rem;
            font-size: 1.1rem;
        }
        a {
            color: #4CAF50;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>🔗 Create Your Short Link</h2>
        <form method="post">
            <input type="text" name="url" placeholder="Paste your long URL here..." required>
            <br>
            <input type="submit" value="Shorten URL">
        </form>
        {% if short_url %}
        <div class="result">
            <p>✅ Short URL: <a href="{{ short_url }}" target="_blank">{{ short_url }}</a></p>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

# ✅ This part ensures your app works on Render or any other platform
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 for local
    app.run(host="0.0.0.0", port=port, debug=True)
