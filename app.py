#coding=utf-8
from flask import (Flask, request, render_template, send_from_directory,
                   jsonify, session)
from werkzeug.utils import secure_filename
import os
import json
import logging
from src.es_models import EsModel
from src.database.connect import connect_es
from src.models import TensorflowModel, CaffeModel, OnnxModel
from src.tasks import ConvertConsumer, UploadConsumer, UploadProducer, ConvertProducer
import queue
import time

uploading_queue = queue.Queue(maxsize=2)
uploaded_queue = queue.Queue(maxsize=100)
model_pool = dict()
isHaveOne = 'aaaaaaaaaa'
model_id = ''

base_dir = os.path.abspath(os.path.dirname(__file__))
upload_base_dir = os.path.join(base_dir, 'upload/')
convert_base_dir = os.path.join(base_dir, 'save_model/')

app = Flask(__name__)


def create_app(app):
    app.debug = True
    app.config['SECRET_KEY'] = os.urandom(24)
    handler = logging.FileHandler('x2paddle.log', encoding='UTF-8')
    handler.setLevel(logging.DEBUG)
    format = logging.Formatter("[%(asctime)s] %(levelname)-8s %(message)s",
                               "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(format)
    app.logger.name = 'x2paddle'
    app.logger.addHandler(handler)
    return app


def create_model(request, session, isHaveOne):
    suffix = request.files['file'].filename.split('.')[-1]

    model = None
    if suffix == 'pb':
        model = TensorflowModel(upload_base_dir, convert_base_dir, request)
    elif suffix == 'onnx':
        model = OnnxModel(upload_base_dir, convert_base_dir, request)
    elif suffix in ['caffemodel', 'prototxt', 'proto', 'pt']:
        if isHaveOne == 'aaaaaaaaaa':
            model = CaffeModel(upload_base_dir, convert_base_dir, request,
                               isHaveOne)
        else:
            model = CaffeModel(upload_base_dir, convert_base_dir, request,
                               isHaveOne)
            isHaveOne = 'aaaaaaaaaa'

    model_pool[model.id] = model
    # In the future, paddle2onnx may be supported

    return model


def get_model(id):
    return model_pool[id]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        uploaded_files = request.files.getlist("file")
        try:
            isHaveOne = request.form['model_id']
        except:
            isHaveOne = 'aaaaaaaaaa'

        model = create_model(request, session, isHaveOne)
        # session['id'] = model.id

        if not model.check_filetype():
            return jsonify(status='failed', message='filetype error')

        # initial database object
        es_model = EsModel(meta={'id': model.id}, ip=request.remote_addr)
        es_model.save()

        producer = UploadProducer('Producer', uploading_queue, model_pool, app)
        if producer.add_task(model):
            producer.start()
            producer.join()
            # return jsonify(model.uploaded)
            return jsonify(name=model.id, status='success', message='uploaded')
        else:
            return jsonify(name=model.id, status='failed', message='waiting')


@app.route('/convert', methods=['POST'])
def convert():
    # model = get_model(session)
    data = json.loads(request.get_data().decode('utf-8'))
    model = get_model(data['model_id'])
    global model_id
    model_id = data['model_id']
    es_model = EsModel.get(id=model.id)
    es_model.update(email=data['email'])
    es_model.update(framework=data['framework'])
    es_model.update(model_class=data['model_class'])
    localtime = time.localtime(time.time())
    es_model.update(time=localtime)

    producer = ConvertProducer('Producer', uploaded_queue, model_pool, app)
    if producer.add_task(model):
        producer.start()
        producer.join()
        return jsonify(model.result)
    else:
        return jsonify(name=model.id, status='failed', message='waiting')


@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    # id = session.get('id')
    id = model_id
    download_dir = os.path.join(convert_base_dir, id)
    return send_from_directory(directory=download_dir, filename=filename)


@app.route('/testdata/<path:filename>', methods=['GET', 'POST'])
def testdata(filename):
    updir = os.path.join(base_dir, 'upload/')
    return send_from_directory(directory=updir, filename=filename)


if __name__ == '__main__':
    #connect es
    config_dir = 'src/database/config.json'
    try:
        with open(config_dir) as f:
            config = json.loads(f.read())
            f.close()
    except:
        assert 'fail to load config: ' + config_dir
    connect_es(config)

    #initial server
    app = create_app(app)

    #create consumer
    uploadConsumer = UploadConsumer('uploadConsumer', uploading_queue,
                                    model_pool, app)
    uploadConsumer.start()

    uploadConsumer = UploadConsumer('uploadConsumer', uploading_queue,
                                    model_pool, app)
    uploadConsumer.start()

    uploadConsumer = UploadConsumer('uploadConsumer', uploading_queue,
                                    model_pool, app)
    uploadConsumer.start()

    convertConsumer = ConvertConsumer('convertConsumer', uploaded_queue,
                                      model_pool, app)
    convertConsumer.start()

    convertConsumer = ConvertConsumer('convertConsumer', uploaded_queue,
                                      model_pool, app)
    convertConsumer.start()

    convertConsumer = ConvertConsumer('convertConsumer', uploaded_queue,
                                      model_pool, app)
    convertConsumer.start()

    app.run(host='0.0.0.0', port=8120)
