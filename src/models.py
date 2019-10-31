import uuid
import os
from werkzeug.utils import secure_filename
import sys
from subprocess import Popen, PIPE, STDOUT


def run_script(cmd, model_name, save_base_dir):
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
        self.save_dir = save_dir

    def convert(self):
        filename = self.file['filename']
        save_base_dir = os.path.join(self.convert_base_dir, self.id)
        cmd = 'x2paddle' + ' --framework=onnx' + ' --model=' + self.file[
            'upload_dir'] + ' --save_dir=' + self.save_dir
        return run_script(cmd, filename, save_base_dir)


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
        save_base_dir = os.path.join(self.convert_base_dir, self.id)
        self.save_dir = os.path.join(save_base_dir + '/' +
                                     self.file['filename'])

    def convert(self):
        filename = self.file['filename']
        save_base_dir = os.path.join(self.convert_base_dir, self.id)

        cmd = 'x2paddle' + ' --framework=tensorflow' + ' --model=' + self.file[
            'upload_dir'] + ' --save_dir=' + self.save_dir
        return run_script(cmd, filename, save_base_dir)


class CaffeModel():
    def __init__(self, upload_base_dir, convert_base_dir, request):
        self.id = uuid.uuid4().hex
        self.framework = ''
        self.headers = request.headers
        self.upload_base_dir = upload_base_dir
        self.convert_base_dir = convert_base_dir
        self.files = {
            'caffe_weight': {
                'object': None,
                'upload_dir': '',
                'filename': '',
            },
            'caffe_model': {
                'object': None,
                'upload_dir': '',
                'filename': '',
            }
        }
        self.resolve_files(request)

    def resolve_files(self, request):
        if 'caffe_weight' in request.files:
            self.files['caffe_weight']['object'] = request.files[
                'caffe_weight']
            self.files['caffe_weight']['filename'] = request.files[
                'caffe_weight'].filename.split('.')[0]
        if 'caffe_model' in request.files:
            self.files['caffe_model']['object'] = request.files['caffe_model']
            self.files['caffe_model']['filename'] = request.files[
                'caffe_model'].filename.split('.')[0]

    def save(self):
        updir = os.path.join(self.upload_base_dir, self.id)
        if not os.path.exists(updir):
            os.mkdir(updir)
        caffe_weight = self.files['caffe_weight']['object']
        caffe_model = self.files['caffe_model']['object']
        caffe_weight_filename = secure_filename(caffe_weight.filename)
        caffe_model_filename = secure_filename(caffe_model.filename)
        caffe_weight_dir = os.path.join(updir, caffe_weight_filename)
        caffe_model_dir = os.path.join(updir, caffe_model_filename)
        caffe_weight.save(caffe_weight_dir)
        self.files['caffe_weight']['upload_dir'] = caffe_weight_dir
        caffe_model.save(caffe_model_dir)
        self.files['caffe_model']['upload_dir'] = caffe_model_dir
        save_base_dir = os.path.join(self.convert_base_dir, self.id)
        save_dir = os.path.join(save_base_dir + '/' +
                                self.files['caffe_model']['filename'])

    def convert(self):
        filename = self.files['caffe_model']['filename']
        save_base_dir = os.path.join(self.convert_base_dir, self.id)
        save_dir = self.files['caffe_model']['save_dir']
        weight_path = os.path.join(self.files['caffe_weight']['upload_dir'])
        model_path = os.path.join(self.files['caffe_model']['upload_dir'])
        cmd = 'x2paddle' + ' --framework=caffe' + ' --prototxt=' + model_path + \
            ' --weight=' + weight_path + ' --save_dir=' + save_dir
        return run_script(cmd, filename, save_base_dir)

    def check_filetype(self):
        weight_name = self.files['caffe_weight']['object'].filename
        model_name = self.files['caffe_model']['object'].filename

        caffe_model_support_type = ['prototxt', 'proto', 'pt']

        valid_weight_name = '.' in weight_name and weight_name.split(
            '.')[-1] == 'caffemodel'

        valid_model_name = '.' in model_name and model_name.split(
            '.')[-1] in caffe_model_support_type

        return valid_weight_name and valid_model_name
