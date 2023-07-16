from pathlib import Path
from uuid import uuid4

from flask import Flask, request, send_file
from flask_cors import CORS
from flask_uuid import FlaskUUID

app = Flask(__name__)
CORS(app)
FlaskUUID(app)


@app.route('/health')
def health():
    return 200


@app.route('/image-upload', methods=['POST'])
def upload_file():
    f = request.files['file']
    filename = str(uuid4())
    f.save(Path('dl').joinpath(filename))
    return filename


@app.route('/i/<uuid:image_id>', methods=['GET'])
def get_image(image_id):
    return send_file(Path('dl').joinpath(str(image_id)), mimetype='image/jpeg')


if __name__ == '__main__':
    app.run(debug=True)
