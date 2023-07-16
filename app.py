from pathlib import Path
from uuid import uuid4

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from flask_uuid import FlaskUUID

app = Flask(__name__)
CORS(app)
FlaskUUID(app)


@app.route('/health')
def health():
    return jsonify(success=True)


@app.route('/image-upload', methods=['POST'])
def upload_file():
    f = request.files['file']
    path = Path('dl')
    path.mkdir(exist_ok=True)
    while (filename := path.joinpath(str(uuid4()))).exists():
        print(f'file [{filename}] exists, regenerating...')
        pass
    f.save(filename)
    return filename


@app.route('/i/<uuid:image_id>', methods=['GET'])
def get_image(image_id):
    filename = Path('dl').joinpath(str(image_id))
    if filename.exists():
        return send_file(filename, mimetype='image/jpeg')
    else:
        return jsonify({'error': f'image [{image_id}] does not exists'})


if __name__ == '__main__':
    app.run(debug=True)
