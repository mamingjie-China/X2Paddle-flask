from elasticsearch_dsl import  Document, Keyword ,Text,Ip

class EsModel(Document):
    ip= Text()
    email = Text()
    log = Text()
    model_dir = Text()
    framework = Text()
    class Index:
        name = 'flask'
    def save(self, ** kwargs):
        return super(EsModel, self).save(** kwargs)
