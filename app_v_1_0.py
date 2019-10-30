#coding=utf-8
from flask import (Flask, request, render_template, send_from_directory,
                   jsonify, session)
from werkzeug.utils import secure_filename
import os
import json
from subprocess import Popen, PIPE, STDOUT
import sys
import logging
from src.es_models import EsModel
from src.database.connect import connect_es
import uuid

basedir = os.path.abspath(os.path.dirname(__file__))
convert_base_dir = os.path.join(basedir, 'save_model/')

app = Flask(__name__)


def initial_app(app):
    app.debug = True
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['ALLOWED_EXTENSIONS'] = set(
        ['onnx', 'pb', 'caffemodel', 'prototxt', 'pt', 'proto'])
    handler = logging.FileHandler('x2paddle.log', encoding='UTF-8')
    handler.setLevel(logging.DEBUG)
    format = logging.Formatter("[%(asctime)s] %(levelname)-8s %(message)s",
                               "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(format)
    app.logger.name = 'x2paddle'
    app.logger.addHandler(handler)
    return app


def check_file_extension(filename):
    return '.' in filename and filename.split(
        '.')[-1] in app.config['ALLOWED_EXTENSIONS']


def x2paddle(cmd, model_name, save_base_dir):
    save_dir = os.path.join(save_base_dir, model_name)
    p = Popen(cmd,
              stdout=PIPE,
              stderr=STDOUT,
              shell=True,
              universal_newlines=True)
    cmd_result = ''
    for line in p.stdout.readlines():
        if 'Converting node' in line:
            continue
        cmd_result += str(line).rstrip() + '<br/>\n'
        sys.stdout.flush()
    # zip_dir = os.path.join(save_dir, model_name + '.tar.gz')
    zip_dir = save_dir + '.tar.gz'
    #    zip_dir = model_name + '.tar.gz'
    es_model = EsModel.get(id=session.get('id'))
    es_model.update(log=cmd_result)

    if os.path.exists(os.path.join(save_dir, 'inference_model/__model__')):
        os.system('tar -C ' + save_base_dir + ' -zcvf ' + zip_dir + ' ' +
                  model_name)
        app.logger.info(model_name + ' convert success')
        return jsonify(name=model_name + '.tar.gz',
                       status='success',
                       cmd_result=cmd_result)
    else:
        app.logger.info(model_name + ' convert failed')
        return jsonify(name='', status='failed', cmd_result=cmd_result)


import queue
import threading, time
threading.stack_size(65536)
uploading_queue = queue.Queue(maxsize=10)
uploaded_queue = queue.Queue(maxsize=100)


class Producer(threading.Thread):
    def __init__(self, name, wait_queue, finish_queue, app):
        self.id = None
        self.wait_queue = wait_queue
        self.finish_queue = finish_queue
        threading.Thread.__init__(self, name=name)
        self.daemon = True
        self.app = app

    def add_task(self, file):
        print("%s is producing %s to the queue!" %
              (threading.current_thread(), file.filename))
        # self.id = file.filename
        self.id = session.get('id')
        message = (self.id, file)
        if self.wait_queue.full():
            return False
        self.wait_queue.put(message)
        print("%s finished!" % self.getName())
        return True

    def run(self):
        while True:
            id = self.finish_queue.get()
            if self.id == id:
                break
        app.logger.info('producer get ack success')


class Consumer(threading.Thread):
    def __init__(self, name, wait_queue, finish_queue):
        threading.Thread.__init__(self, name=name)
        self.wait_queue = wait_queue
        self.finish_queue = finish_queue
        self.daemon = True

    def run(self):
        while True:
            id, file = self.wait_queue.get()
            print("%s is consuming. %s in the queue is consumed!" %
                  (self.getName(), file.filename))
            filename = secure_filename(file.filename)
            app.logger.info('FileName: ' + filename)
            updir = os.path.join(basedir, 'upload/')
            updir = os.path.join(updir, id)
            if not os.path.exists(updir):
                os.mkdir(updir)
            file.save(os.path.join(updir, filename))
            self.finish_queue.put(id)
            app.logger.info('upload success')


@app.route('/')
def index():
    app.logger.info(request.remote_addr + ' login')
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    #获取用户ip地址
    app.logger.info('start upload')
    start_time = time.time()
    # id = str(start_time) + '_' + request.remote_addr
    id = uuid.uuid4().hex
    es_model = EsModel(meta={'id': id}, ip=request.remote_addr)
    es_model.save()
    session['id'] = id
    if request.method == 'POST':
        file = request.files['file']
        if file and check_file_extension(file.filename):
            app.logger.info('file type is allow')
            producer = Producer('Producer', uploading_queue, uploaded_queue,
                                app)
            if producer.add_task(file):
                producer.start()
                producer.join()
            else:
                return jsonify(name=file.filename, status='waited')
            print(threading.enumerate())
            updir = os.path.join(basedir, 'upload/')
            updir = os.path.join(updir, id)
            es_model = EsModel.get(id=session.get('id'))
            es_model.update(models_dir=os.path.join(updir, file.filename))
            return jsonify(name=file.filename, status='success')


@app.route('/convert', methods=['POST'])
def convert():
    '''
    {0:'tensorflow',1:'onnx',2:'caffe'}
    :return:
    '''
    print(request.get_data(), 123456)
    data = json.loads(request.get_data().decode('utf-8'))

    id = session.get('id')
    updir = os.path.join(basedir, 'upload/')
    updir = os.path.join(updir, id)
    es_model = EsModel.get(id=id)
    es_model.update(email=data['email'])
    es_model.update(framework=data['framework'])
    app.logger.info('start convert')

    if data['framework'] == '0':
        #tensorflow
        model_full_name = data['tf_name']
        if model_full_name == '':
            return jsonify(status='failed')
        save_base_dir = os.path.join(convert_base_dir, id)
        model_name = model_full_name.split('.')[0]
        save_dir = os.path.join(save_base_dir, model_name)
        model_path = os.path.join(updir, model_full_name)
        cmd = 'x2paddle' + ' --framework=tensorflow' + ' --model=' + model_path + ' --save_dir=' + save_dir
        return x2paddle(cmd, model_name, save_base_dir)

    elif data['framework'] == '1':
        #onnx
        model_full_name = data['onnx_name']
        if model_full_name == '':
            return jsonify(status='failed')
        save_base_dir = os.path.join(convert_base_dir, id)
        model_name = model_full_name.split('.')[0]
        save_dir = os.path.join(save_base_dir, model_name)
        model_path = os.path.join(updir, model_full_name)
        cmd = 'x2paddle' + ' --framework=onnx' + ' --model=' + model_path + ' --save_dir=' + save_dir
        return x2paddle(cmd, model_name, save_base_dir)

    elif data['framework'] == '1':
        # caffe
        caffe_weight_name = data['caffe_weight_name']
        caffe_model_name = data['caffe_model_name']
        if caffe_weight_name == '' or caffe_model_name == '':
            return jsonify(status='failed')
        save_base_dir = os.path.join(convert_base_dir, id)
        model_name = caffe_model_name.split('.')[0]
        save_dir = os.path.join(save_base_dir, model_name)
        weight_path = os.path.join(updir, caffe_weight_name)
        model_path = os.path.join(updir, caffe_model_name)
        cmd = 'x2paddle' + ' --framework=caffe' + ' --prototxt=' + model_path + ' --weight=' + weight_path + ' --save_dir=' + save_dir

        return x2paddle(cmd, model_name, save_base_dir)


@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    #    filename = filename[:-7] + '/' + filename
    id = session.get('id')
    download_dir = os.path.join(convert_base_dir, id)
    return send_from_directory(directory=download_dir, filename=filename)


@app.route('/testdata/<path:filename>', methods=['GET', 'POST'])
def testdata(filename):
    updir = os.path.join(basedir, 'upload/')
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
    app = initial_app(app)

    #create consumer
    consumer = Consumer('Consumer', uploading_queue, uploaded_queue)
    consumer.start()

    app.run()
