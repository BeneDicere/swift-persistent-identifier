def sample_app(environ, start_response):
    body = []
    keys = ['PATH_INFO', 'QUERY_STRING', 'REQUEST_METHOD',
            'HTTP_HEADERNAME', 'wsgi.input']
    for key in keys:
        value = environ.get(key)
        body.append('{}: \'{}\'\n'.format(key, value))
    if environ.get('HTTP_X_OBJECT_META_PID'):
        body.append('HTTP_X_OBJECT_META_PID: \'{}\'\n'.
                    format(environ.get('HTTP_X_OBJECT_META_PID')))

    headers = [('Content-Type', 'text/plain')]
    start_response('201 Created', headers)
    return body


def app_factory(global_config, **local_config):
    return sample_app

if __name__ == '__main__':
    from paste import httpserver
    from paste.deploy import loadapp
    wsgi_app = loadapp('config:test/config.ini', relative_to='.')
    httpserver.serve(wsgi_app, host='127.0.0.1', port='8080')
