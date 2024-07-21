from flask import Flask, jsonify
from flask_cors import CORS
import os
import json

app = Flask(__name__)
cors = CORS(app)

PORT = 5000


@app.route('/api/posts', methods=['GET'])
def get_posts():
    json_file_path = os.path.join(os.path.dirname(__file__), 'posts.json')
    try:
        with open(json_file_path, 'r', encoding='utf8') as json_file:
            posts = json.load(json_file)
        return jsonify(posts)
    except FileNotFoundError:
        print(f"Error: {json_file_path} not found.")
        return jsonify({'error': 'Failed to retrieve posts'}), 500
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        return jsonify({'error': 'Invalid JSON format'}), 500
    except Exception as err:
        print(f"Error reading JSON file: {err}")
        return jsonify({'error': 'Failed to retrieve posts'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
