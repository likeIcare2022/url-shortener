from flask import Flask, render_template, request, redirect, jsonify
import json
import random
import string
from datetime import datetime

app = Flask(__name__)
URL_DB_FILE = 'urls.json'


# Helper functions

def load_url_db():
    try:
        with open(URL_DB_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_url_db(data):
    with open(URL_DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)


def shorten_url_helper(url):
    # Generate a random short code
    short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    return short_code


def short_url_exists(short_code):
    url_db = load_url_db()
    return short_code in url_db


def save_url_mapping(short_code, original_url, expiration_date):
    url_db = load_url_db()
    url_db[short_code] = {
        'original_url': original_url,
        'expiration_date': expiration_date
    }
    save_url_db(url_db)


def is_valid_custom_code(code):
    # Validate custom short code (example: must be alphanumeric and not already in use)
    url_db = load_url_db()
    return code.isalnum() and not short_url_exists(code)


# Routes

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/shorten', methods=['POST'])
def shorten_url():
    original_url = request.form['urlInput']
    custom_short_code = request.form['customShortCode']
    expiration_date = request.form['expirationDate']

    if custom_short_code and not is_valid_custom_code(custom_short_code):
        return jsonify({'error': 'Custom short code must be alphanumeric and not already in use.'}), 400

    if custom_short_code:
        short_url = custom_short_code
    else:
        short_url = shorten_url_helper(original_url)

    save_url_mapping(short_url, original_url, expiration_date)

    return jsonify({'short_url': f'http://localhost:5000/{short_url}'})


@app.route('/all_urls')
def all_urls():
    url_db = load_url_db()
    return render_template('all_urls.html', urls=url_db)


@app.route('/delete/<short_url>', methods=['POST'])
def delete_url(short_url):
    url_db = load_url_db()
    if short_url in url_db:
        del url_db[short_url]
        save_url_db(url_db)
        return jsonify({'message': 'URL deleted successfully'})
    else:
        return jsonify({'error': 'URL not found'}), 404


@app.route('/<short_url>')
def redirect_to_url(short_url):
    url_db = load_url_db()
    if short_url in url_db:
        original_url = url_db[short_url]['original_url']
        return redirect(original_url)
    else:
        return 'URL not found', 404


if __name__ == '__main__':
    app.run(debug=True)
