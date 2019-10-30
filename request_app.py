import requests
import threading
class Request2(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
  def run(self):
    file1 = {
      "tensorflow": open("/Users/chenlingchi/Downloads/onet-18.pb", "rb")
    }
    r1 = requests.post('http://127.0.0.1:5000/x2paddle', files=file1, data={'framework': 'tensorflow'})
    print(self.name, r1.json())
class Request3(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
  def run(self):
    file1 = {
      "tensorflow": open("/Users/chenlingchi/Downloads/onet-18.pb", "rb")
    }
    r1 = requests.post('http://127.0.0.1:5000/x2paddle', files=file1, data={'framework': 'tensorflow'})
    print(self.name, r1.json())


class Request4(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
  def run(self):
    file1 = {
      "tensorflow": open("/Users/chenlingchi/Downloads/onet-18.pb", "rb")
    }
    r1 = requests.post('http://127.0.0.1:5000/x2paddle', files=file1, data={'framework': 'tensorflow'})
    print(self.name, r1.json())

class Request5(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
  def run(self):
    file1 = {
      "tensorflow": open("/Users/chenlingchi/Downloads/onet-18.pb", "rb")
    }
    r1 = requests.post('http://127.0.0.1:5000/x2paddle', files=file1, data={'framework': 'tensorflow'})
    print(self.name, r1.json())

class Request1(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
  def run(self):
    file1 = {
      "onnx": open("/Users/chenlingchi/Documents/person_git/X2Paddle/onnx_model_supported/classification/Face_cyclegan_34.onnx", "rb")
    }
    r1 = requests.post('http://127.0.0.1:5000/x2paddle', files=file1, data={'framework': 'onnx'})
    print(self.name, r1.json())

if __name__ == '__main__':
  request1 = Request1()
  request2 = Request2()
  request3 = Request3()
  request4 = Request4()
  request5 = Request5()
  request1.start()
  # request2.start()
  # request4.start()
  # request3.start()
  # request5.start()

  # request2.join()
  # request1.join()
  # request4.join()
  # request3.join()
  # request5.join()
