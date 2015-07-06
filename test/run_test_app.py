def sample_app(environ, start_response):
    body = []
    keys = ['PATH_INFO', 'QUERY_STRING', 'REQUEST_METHOD',
            'HTTP_HEADERNAME', 'wsgi.input']
    if 'debug' in environ['QUERY_STRING']:
        for key in keys:
            value = environ.get(key)
            body.append('{}: \'{}\'\n'.format(key, value))
        headers = [('Content-Type', 'text/plain')]
    else:
        headers = []
    if 'notfound' in environ['QUERY_STRING']:
        status = '404 Not Found'
    else:
        status = '201 Created'
    start_response(status, headers)
    return body


def app_factory(global_config, **local_config):
    return sample_app

if __name__ == '__main__':
    from paste import httpserver
    from paste.deploy import loadapp
    wsgi_app = loadapp('config:test/config.ini', relative_to='.')
    httpserver.serve(wsgi_app, host='127.0.0.1', port='8080')
