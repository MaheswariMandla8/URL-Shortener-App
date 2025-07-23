from flask import Flask, jsonify, request, redirect, abort
from flask.views import MethodView
from datetime import datetime
import threading
import string
import random
import re

app = Flask(__name__)

# ─── In-Memory Store and Lock ───
url_store = {}
click_store = {}
lock = threading.Lock()

# ─── Constants ───
SHORT_CODE_LENGTH = 6
BASE_URL = "http://localhost:5000"

# ─── Utilities ───
def generate_short_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=SHORT_CODE_LENGTH))

def is_valid_url(url):
    regex = re.compile(
        r'^(https?|ftp):\/\/(?!-)[A-Za-z0-9.-]+(?<!-)\.[A-Za-z]{2,}(\/\S*)?$'
    )
    return re.match(regex, url) is not None

# ─── RESTful Resources ───
class HealthAPI(MethodView):
    def get(self):
        return jsonify({"status": "healthy", "service": "URL Shortener API"})

class ShortenAPI(MethodView):
    def post(self):
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "Missing 'url' in request body"}), 400

        long_url = data['url']
        if not is_valid_url(long_url):
            return jsonify({"error": "Invalid URL format"}), 400

        with lock:
            short_code = generate_short_code()
            while short_code in url_store:
                short_code = generate_short_code()

            url_store[short_code] = {
                'url': long_url,
                'created_at': datetime.utcnow().isoformat()
            }
            click_store[short_code] = 0

        return jsonify({
            "short_code": short_code,
            "short_url": f"{BASE_URL}/{short_code}"
        })

class RedirectAPI(MethodView):
    def get(self, short_code):
        with lock:
            if short_code not in url_store:
                abort(404)

            click_store[short_code] += 1
            long_url = url_store[short_code]['url']

        return redirect(long_url)

class StatsAPI(MethodView):
    def get(self, short_code):
        with lock:
            if short_code not in url_store:
                return jsonify({"error": "Short code not found"}), 404

            data = url_store[short_code]
            clicks = click_store.get(short_code, 0)

        return jsonify({
            "url": data['url'],
            "clicks": clicks,
            "created_at": data['created_at']
        })

# ─── Register Routes ───
app.add_url_rule('/', view_func=HealthAPI.as_view('health_api'))
app.add_url_rule('/api/shorten', view_func=ShortenAPI.as_view('shorten_api'))
app.add_url_rule('/<string:short_code>', view_func=RedirectAPI.as_view('redirect_api'))
app.add_url_rule('/api/stats/<string:short_code>', view_func=StatsAPI.as_view('stats_api'))

if __name__ == '__main__':
    app.run(debug=True)