import threading, time
threading.stack_size(65536)


class UploadProducer(threading.Thread):
    def __init__(self, name, wait_queue, model_pool, app):
        threading.Thread.__init__(self, name=name)
        self.id = None
        self.wait_queue = wait_queue
        self.model_pool = model_pool
        self.daemon = True
        self.result = None
        self.app = app

    def add_task(self, model):
        print("producing %s to the queue!" % (model.id))
        self.id = model.id
        if self.wait_queue.full():
            return False
        self.wait_queue.put(model)
        print("%s finished!" % self.getName())
        return True

    def run(self):
        while True:
            time.sleep(1)
            if self.model_pool[self.id].uploaded == True:
                self.app.logger.info(self.id + ' UploadProducer get ack success')
                break

class ConvertProducer(threading.Thread):
    def __init__(self, name, wait_queue, model_pool, app):
        threading.Thread.__init__(self, name=name)
        self.id = None
        self.wait_queue = wait_queue
        self.model_pool = model_pool
        self.daemon = True
        self.result = None
        self.app = app

    def add_task(self, model):
        print("producing %s to the queue!" % (model.id))
        self.id = model.id
        if self.wait_queue.full():
            return False
        self.wait_queue.put(model)
        print("%s finished!" % self.getName())
        return True

    def run(self):
        while True:
            time.sleep(1)
            if self.model_pool[self.id].converted == True:
                self.app.logger.info(self.id + ' ConvertProducer get ack success')
                break

class UploadConsumer(threading.Thread):
    def __init__(self, name, wait_queue, finish_pool, app):
        threading.Thread.__init__(self, name=name)
        self.wait_queue = wait_queue
        self.finish_pool = finish_pool
        self.daemon = True
        self.app = app

    def run(self):
        while True:
            time.sleep(1)
            model = self.wait_queue.get()
            self.app.logger.info('start upload')
            self.app.logger.info(
                "%s is consuming. %s in the queue is consumed!" %
                (self.getName(), model.id))
            model.save()
            model.uploaded = True
            self.app.logger.info('upload success')


class ConvertConsumer(threading.Thread):
    def __init__(self, name, wait_queue, model_pool, app):
        threading.Thread.__init__(self, name=name)
        self.wait_queue = wait_queue
        self.model_pool = model_pool
        self.daemon = True
        self.app = app

    def run(self):
        while True:
            time.sleep(1)
            model = self.wait_queue.get()
            self.app.logger.info('start convert')
            self.app.logger.info(
                "%s is consuming. %s in the queue is consumed!" %
                (self.getName(), model.id))
            result = model.convert()
            model.converted=True
            model.result = result
            self.app.logger.info('convert done')
