import os
import logging
from flask import Flask, request, render_template, Response

app = Flask(__name__, static_folder="static", static_url_path="")

@app.route('/', methods=['GET'])
def index() -> str:
    return render_template('index.html')

if __name__ == '__main__':
    # logging.basicConfig(level=logging.INFO)
    app.run(host='127.0.0.1', port=8080, debug=True)