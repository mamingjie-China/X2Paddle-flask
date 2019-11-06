import uuid
import os
from werkzeug.utils import secure_filename
import sys
from subprocess import Popen, PIPE, STDOUT
from src.es_models import EsModel


def run_script(cmd, model_name, save_base_dir, id):
    p = Popen(cmd,
              stdout=PIPE,
              stderr=STDOUT,
              shell=True,
              universal_newlines=True)
    cmd_result = ''
    for line in p.stdout.readlines():
        if "Converting node" in line:
            continue
        cmd_result += str(line).rstrip() + '<br/>\n'
        sys.stdout.flush()

    zip_dir = os.path.join(save_base_dir, model_name + '.tar.gz')
    save_dir = os.path.join(save_base_dir, model_name)

    es_model = EsModel.get(id=id)
    es_model.update(log=cmd_result)
    es_model.update(save_dir=save_dir)

    if os.path.exists(os.path.join(save_dir, 'inference_model/__model__')):
        os.system('tar -C ' + save_base_dir + ' -cvzf ' + zip_dir + ' ' +
                  model_name)
        res = {
            'name': model_name + '.tar.gz',
            'status': 'success',
            'cmd_result': cmd_result
        }
        return res
    else:
        res = {'status': 'failed', 'cmd_result': cmd_result}
        return res


class Model():
    def __init__(self, upload_base_dir, convert_base_dir, request):
        self.id = uuid.uuid4().hex
        self.framework = ''
        self.headers = request.headers
        self.file = {
            'object': None,
            'upload_dir': '',
            'filename': '',
        }
        self.uploaded = False
        self.converted = False
        self.result = ''
        self.upload_base_dir = upload_base_dir
        self.convert_base_dir = convert_base_dir
        self.save_dir = ''

    def check_filetype(self):
        support_type = ['onnx', 'pb', 'caffemodel', 'prototxt', 'proto', 'pt']

        return '.' in self.file['object'].filename and self.file[
            'object'].filename.split('.')[-1] in support_type


class OnnxModel(Model):
    def __init__(self, upload_base_dir, convert_base_dir, request):
        super(OnnxModel, self).__init__(upload_base_dir, convert_base_dir,
                                        request)
        self.resolve_files(request)

    def resolve_files(self, request):
        if 'file' in request.files:
            obj = request.files['file']
            self.file['object'] = obj
            self.file['filename'] = obj.filename.split('.')[0]

    def save(self):
        updir = os.path.join(self.upload_base_dir, self.id)
        if not os.path.exists(updir):
            os.mkdir(updir)
        file = self.file['object']
        filename = secure_filename(file.filename)
        file_dir = os.path.join(updir, filename)
        file.save(file_dir)
        self.file['upload_dir'] = file_dir
        save_base_dir = os.path.join(self.convert_base_dir, self.id)
        save_dir = os.path.join(save_base_dir + '/' + self.file['filename'])
        file_size = os.path.getsize(file_dir)

        es_model = EsModel.get(id=self.id)
        es_model.update(upload_dir=file_dir)
        es_model.update(file_size=file_size)

        self.save_dir = save_dir

    def convert(self):
        filename = self.file['filename']
        save_base_dir = os.path.join(self.convert_base_dir, self.id)
        cmd = 'x2paddle' + ' --framework=onnx' + ' --model=' + self.file[
            'upload_dir'] + ' --save_dir=' + self.save_dir
        id = self.id
        return run_script(cmd, filename, save_base_dir, id)


class TensorflowModel(Model):
    def __init__(self, upload_base_dir, convert_base_dir, request):
        super(TensorflowModel, self).__init__(upload_base_dir,
                                              convert_base_dir, request)
        self.resolve_files(request)

    def resolve_files(self, request):
        if 'file' in request.files:
            obj = request.files['file']
            self.file['object'] = obj
            self.file['filename'] = obj.filename.split('.')[0]

    def save(self):
        updir = os.path.join(self.upload_base_dir, self.id)
        if not os.path.exists(updir):
            os.mkdir(updir)
        file = self.file['object']
        filename = secure_filename(file.filename)
        file_dir = os.path.join(updir, filename)
        file.save(file_dir)
        self.file['upload_dir'] = file_dir
        file_size = os.path.getsize(file_dir)

        es_model = EsModel.get(id=self.id)
        es_model.update(upload_dir=file_dir)
        es_model.update(file_size=file_size)

        save_base_dir = os.path.join(self.convert_base_dir, self.id)
        self.save_dir = os.path.join(save_base_dir + '/' +
                                     self.file['filename'])

    def convert(self):
        filename = self.file['filename']
        save_base_dir = os.path.join(self.convert_base_dir, self.id)
        cmd = 'x2paddle' + ' --framework=tensorflow' + ' --model=' + self.file[
            'upload_dir'] + ' --save_dir=' + self.save_dir
        id = self.id
        return run_script(cmd, filename, save_base_dir, id)


class CaffeModel():
    def __init__(self, upload_base_dir, convert_base_dir, request, isOne):
        if isOne == 'aaaaaaaaaa':
            self.id = uuid.uuid4().hex
        else:
            self.id = isOne
        self.framework = ''
        self.headers = request.headers
        self.upload_base_dir = upload_base_dir
        self.convert_base_dir = convert_base_dir
        self.files = {
            'caffe_weight': {
                'object': None,
                'upload_dir': '',
                'filename': '',
                'suffix': '',
                'id': '',
            },
            'caffe_model': {
                'object': None,
                'upload_dir': '',
                'filename': '',
                'suffix': '',
                'id': '',
            }
        }
        self.uploaded = False
        self.converted = False
        self.result = ''
        self.upload_base_dir = upload_base_dir
        self.convert_base_dir = convert_base_dir
        self.save_dir = ''
        self.resolve_files(request)

    def resolve_files(self, request):
        if 'file' in request.files:
            if request.files['file'].filename.split('.')[-1] == 'prototxt':
                self.files['caffe_model'] = request.files['file']
                model_name = request.files['file'].filename
                self.files['caffe_model'].filename = model_name
                self.files['caffe_model'].suffix = model_name.split('.')[-1]

            elif request.files['file'].filename.split('.')[-1] == 'caffemodel':
                self.files['caffe_weight'] = request.files['file']
                model_name = request.files['file'].filename
                self.files['caffe_weight'].filename = model_name
                self.files['caffe_weight'].suffix = model_name.split('.')[-1]

    def save(self):
        updir = os.path.join(self.upload_base_dir, self.id)
        if not os.path.exists(updir):
            os.mkdir(updir)

        try:
            self.files['caffe_weight'].id = self.id
            caffe_weight = self.files['caffe_weight']
            caffe_weight_filename = secure_filename(caffe_weight.filename)
            caffe_weight_dir = os.path.join(updir, caffe_weight_filename)
            caffe_weight.save(caffe_weight_dir)
            self.files['caffe_weight'].upload_dir = caffe_weight_dir
            save_base_dir = os.path.join(self.convert_base_dir, self.id)
            save_dir = os.path.join(save_base_dir + '/' +
                                    self.files['caffe_weight'].filename)
            file_size = os.path.getsize(caffe_weight_dir)

            es_model = EsModel.get(id=self.id)
            es_model.update(upload_dir=caffe_weight_dir)
            es_model.update(file_size=file_size)

            self.save_dir = save_dir
        except:
            self.files['caffe_model'].id = self.id
            caffe_model = self.files['caffe_model']
            caffe_model_filename = secure_filename(caffe_model.filename)
            caffe_model_dir = os.path.join(updir, caffe_model_filename)
            caffe_model.save(caffe_model_dir)
            self.files['caffe_model'].upload_dir = caffe_model_dir
            save_base_dir = os.path.join(self.convert_base_dir, self.id)
            save_dir = os.path.join(save_base_dir + '/' +
                                    self.files['caffe_model'].filename)

            self.save_dir = save_dir

    def convert(self):
        model_path = os.path.join(self.upload_base_dir, self.id)
        for filename in os.listdir(model_path):
            if filename.split('.')[-1] == 'caffemodel':
                caffe_weight_filename = filename
            else:
                caffe_model_filename = filename

        caffe_model_path = os.path.join(model_path, caffe_model_filename)
        caffe_weight_path = os.path.join(model_path, caffe_weight_filename)

        save_base_dir = os.path.join(self.convert_base_dir, self.id)
        save_dir = os.path.join(save_base_dir,
                                caffe_model_filename.split('.')[0])

        id = self.id
        model_name = caffe_model_filename.split('.')[0]

        # save_dir = os.path.join(self.save)

        cmd = 'x2paddle' + ' --framework=caffe' + ' --prototxt=' + caffe_model_path + ' --weight=' + caffe_weight_path + ' --save_dir=' + save_dir
        return run_script(cmd, model_name, save_base_dir, id)

    def check_filetype(self):
        return True
        # weight_suffix = self.files['caffe_weight'].suffix
        # print(weight_suffix,44441111)
        # model_name = self.files['caffe_model'].filename
        #
        # caffe_model_support_type = ['prototxt', 'proto', 'pt']
        # valid_weight_name = '.' in weight_name and weight_name.split(
        #     '.')[-1] == 'caffemodel'
        # valid_model_name = '.' in model_name and model_name.split(
        #     '.')[-1] in caffe_model_support_type
        #
        # return valid_weight_name and valid_model_name
