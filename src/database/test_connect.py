import json
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Search


# Define a default Elasticsearch client
def connect_es(config):
    try:
        es_config = config['es_config']
        user = es_config['user']
        password = es_config['password']
        host = user + ':' + password + '@' + es_config['server']
        connections.create_connection(alias='default', hosts=[host])
    except:
        assert False, 'create connect to database error!!'


with open('config.json') as f:
    config = json.loads(f.read())
    f.close()
connect_es(config)

s = Search(index='flask').query("match_all")
for idx, h in enumerate(s.execute().hits):
    print("-------" + str(idx) + "--------")
    print(h)
    # print(h.meta.id)
    print(h.email)
    # print(h.log)
    # print(h.ip)
    print(h.models_dir)
