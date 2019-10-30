from elasticsearch_dsl.connections import connections


# Define a default Elasticsearch client
def connect_es(config):
    try:
        es_config = config['es_config']
        user = es_config['user']
        password = es_config['password']
        # host = user + ':' + password + '@' + es_config['server']
        host = es_config['server']
        connections.create_connection(alias='default', hosts=[host])
    except:
        assert False, 'create connect to database error!!'


if __name__ == '__main__':
    connections.create_connection(alias='default', hosts=['localhost:9200'])
